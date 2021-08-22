/* クリップをハイライト動画に変換し、S3にアップロードする */

use std::env;
use std::path::PathBuf;

use rusoto_core::{ByteStream, Region, HttpClient};
use rusoto_credential::EnvironmentProvider;
use rusoto_s3::{S3, S3Client, GetObjectRequest, ListObjectsRequest, PutObjectRequest};
use rusoto_ec2::{Ec2, Ec2Client, TerminateInstancesRequest};
use rusoto_sqs::{Sqs, SqsClient, ReceiveMessageRequest, DeleteMessageRequest};
use tokio::io::AsyncReadExt;
use tokio::fs::File;
use tokio::process::Command;
use mysql::*;
use mysql::prelude::*;


#[derive(Debug, Clone)]
struct Highlight {
    task_id: String,
    bucket: String,
    video_key: String,
    transition: String,
    duration: String,
    fl_transition: String,
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
    let sqs_client = SqsClient::new_with(HttpClient::new().unwrap(), provider.clone(), region.clone());
    let ec2_client = Ec2Client::new_with(HttpClient::new().unwrap(), provider.clone(), region.clone());

    // SQSからメッセージを受信する
    let result = sqs_client.receive_message(ReceiveMessageRequest {
        queue_url: env::var("SQS_URL").unwrap(),
        max_number_of_messages: Some(1),
        ..Default::default()
    }).await.unwrap();

    let message = result.messages.unwrap().first().unwrap().clone();
    let task_id = message.body.unwrap();

    // メッセージをSQSから削除
    let _result = sqs_client.delete_message(DeleteMessageRequest {
        queue_url: env::var("SQS_URL").unwrap(),
        receipt_handle: message.receipt_handle.unwrap().clone(),
    }).await.unwrap();

    // RDSから未処理のタスクを１つ抽出し、ステータスを更新する
    let select_task_query = format!("SELECT task_id, bucket, video_key, transition, duration, fl_transition FROM app_digest WHERE task_id='{}'", task_id);
    let tasks = conn.query_map(
        select_task_query,
        |(task_id, bucket, video_key, transition, duration, fl_transition)| {
            Highlight {
                task_id, bucket, video_key, transition, duration, fl_transition
            }
        }
    ).unwrap();

    let task = tasks[0].clone();
    let update_status_query = format!(r"UPDATE app_digest SET status='Processing' WHERE task_id='{}'", task.task_id);
    conn.query_drop(update_status_query).unwrap();

    // クリップをS3からダウンロードする
    let clip_objects = s3_client.list_objects(ListObjectsRequest {
        bucket: task.bucket.clone(),
        prefix: Some(format!("digest/input/input_{}/", task.task_id)),
        ..Default::default()
    }).await.expect("Error while listing clip keys from S3.");

    let home_dir = dirs::home_dir().unwrap();
    let clips_dir = PathBuf::from("clips/");

    let mut clip_paths:Vec<String> = vec![];
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
        let mut abs_path = home_dir.clone();
        let mut clip_path = clips_dir.clone();
        clip_path.push(name.clone());
        abs_path.push(clip_path.clone());
        let mut file = File::create(abs_path.clone()).await.unwrap();
        tokio::io::copy(&mut reader, &mut file).await.unwrap();
        let path_str = clip_path.into_os_string().into_string().unwrap();
        clip_paths.push(path_str);
    }

    let mut input_paths:Vec<&str> = clip_paths.iter().map(AsRef::as_ref).collect();
    // fl_trasition が true なら、前後に黒背景動画を挿入する
    if fl_transition == "1" {
        input_paths.insert(0, "clips/b1s.mp4");
        input_paths.push("clips/b1s.mp4");
    }

    // ffmpeg-concatでハイライト動画を生成する
    let out_file = "output/out.mp4";
    println!("{:?}", input_paths);
    println!("{:?}", out_file);

    let mut command = Command::new("xvfb-run");

    let mut args = vec![];
    args.push("-s");
    args.push(r#"-ac -screen 0 1280x1024x24"#);
    args.push("ffmpeg-concat");
    args.push("-o");
    args.push(out_file);
    args.push("-t");
    args.push(&task.transition);
    args.push("-d");
    args.push(&task.duration);
    args.push("-C");
    args.append(&mut input_paths);

    command.current_dir("/home/ubuntu/").args(args);
    println!("{:?}", command);

    let output = command.output().await.expect("Failed to execute ffmpeg-concat");
    println!("{:?}", output.stdout.iter().map(|ch| *ch as char).collect::<String>());

    // ハイライト動画をS3にアップロードする
    let mut out_path = dirs::home_dir().unwrap();
    out_path.push("output/out.mp4");
    let mut file = File::open(out_path).await.unwrap();
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer).await.unwrap();

    let stream = ByteStream::from(buffer);
    s3_client.put_object(PutObjectRequest {
        bucket: task.bucket.clone(),
        key: task.video_key.clone(),
        body: Some(stream),
        ..Default::default()
    }).await.expect("Error while putting the highlight video.");

    let update_status_query = format!(r"UPDATE app_digest SET status='Uploaded' WHERE task_id='{}'", task.task_id);
    conn.query_drop(update_status_query).unwrap();

    // インスタンスを停止させる
    let output = Command::new("curl")
        .arg("http://169.254.169.254/latest/meta-data/instance-id")
        .output()
        .await
        .expect("Failed to get instance-id.");

    let instance_id = output.stdout.iter().map(|ch| *ch as char).collect::<String>();

    ec2_client.terminate_instances(TerminateInstancesRequest {
        dry_run: None,
        instance_ids: vec![instance_id.clone()]
    }).await.expect("Error while terminating instance");
}
