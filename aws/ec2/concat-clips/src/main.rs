/* クリップをハイライト動画に変換し、S3にアップロードする */

use std::env;
use std::process::Command;

use rusoto_core::{ByteStream, Region, HttpClient};
use rusoto_credential::EnvironmentProvider;
use rusoto_s3::{S3, S3Client, GetObjectRequest, ListObjectsRequest, PutObjectRequest};
use rusoto_ec2::{Ec2, Ec2Client, CancelSpotInstanceRequestsRequest, TerminateInstancesRequest};
use tokio::io::AsyncReadExt;
use tokio::fs::File;
use mysql::*;
use mysql::prelude::*;

struct Highlight {
    task_id: String,
    bucket: String,
    video_key: String,
    transition: String,
    duration: String,
    instance_id: String,
}

#[tokio::main]
async fn main() {
    let db_url = env::var("DATABASE_URL").unwrap();
    let opts = Opts::from_url(&db_url).unwrap();
    let pool = Pool::new(opts).unwrap();
    let mut conn = pool.get_conn().unwrap();

    let region = Region::ApNortheast1;
    let provider = EnvironmentProvider::default();

    let s3_client = S3Client::new_with(HttpClient::new().unwrap(), provider.clone(), region.clone());
    let ec2_client = Ec2Client::new_with(HttpClient::new().unwrap(), provider.clone(), region.clone());

    // RDSから未処理のタスクを１つ抽出し、ステータスを更新する
    let select_task_query = r"SELECT task_id, bucket, video_key, transition, duration, instance_id FROM app_digest WHERE status='Request instance'";
    let tasks = conn.query_map(
        select_task_query,
        |(task_id, bucket, video_key, transition, duration, instance_id)| {
            Highlight {
                task_id, bucket, video_key, transition, duration, instance_id
            }
        }
    ).unwrap();

    let task = &tasks[0];
    let update_status_query = format!(r"UPDATE app_digest SET status='Processing' WHERE task_id='{}'", task.task_id);
    conn.query_drop(update_status_query).unwrap();

    // クリップをS3からダウンロードする
    let clip_objects = s3_client.list_objects(ListObjectsRequest {
        bucket: task.bucket.clone(),
        prefix: Some(format!("digest/input/input_{}/", task.task_id)),
        ..Default::default()
    }).await.expect("Error while listing clip keys from S3.");

    let mut clip_paths = vec![];
    for object in clip_objects.contents.unwrap() {
        let key = object.key.unwrap();
        let name = key.clone();
        let name = name.split('/').last().unwrap();

        let result = s3_client.get_object(GetObjectRequest {
            bucket: task.bucket.clone(),
            key: key,
            ..Default::default()
        }).await.unwrap();
        let mut reader = result.body.unwrap().into_async_read();
        let path = format!("clips/{}", name);
        let mut file = File::create(path.clone()).await.unwrap();
        tokio::io::copy(&mut reader, &mut file).await.unwrap();
        clip_paths.push(path);
    }

    // ffmpeg-concatでハイライト動画を生成する
    let clip_paths = clip_paths.join(" ");
    let output = Command::new("ffmpeg-concat")
        .arg(format!("-t {}", task.transition))
        .arg(format!("-d {}", task.duration))
        .arg("-C")
        .arg(clip_paths)
        .output()
        .expect("Failed to execute ffmpeg-concat.");

    println!("{}", output.stdout.iter().map(|ch| *ch as char).collect::<String>());

    // ハイライト動画をS3にアップロードする
    let mut file = File::open("out.mp4").await.unwrap();
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer).await.unwrap();

    let stream = ByteStream::from(buffer);
    s3_client.put_object(PutObjectRequest {
        bucket: task.bucket.clone(),
        key: task.video_key.clone(),
        body: Some(stream),
        ..Default::default()
    }).await.expect("Error while putting the highlight video.");

    // インスタンスを停止させる
    ec2_client.cancel_spot_instance_requests(CancelSpotInstanceRequestsRequest {
        dry_run: None,
        spot_instance_request_ids: vec![task.instance_id.clone()]
    }).await.expect("Error while canceling spot instance request.");

    ec2_client.terminate_instances(TerminateInstancesRequest {
        dry_run: None,
        instance_ids: vec![task.instance_id.clone()]
    }).await.expect("Error while terminating instance");
}
