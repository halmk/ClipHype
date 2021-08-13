/*
 input: an uploaded clip of input directory
 ( cliphype: digest/input/input_<task_id>/<creator>_<num>.mp4 )

 process: if input clips complete, function sends a message to sqs with task_id

*/

console.log('Loading function');

const aws = require('aws-sdk');
const s3 = new aws.S3({ apiVersion: '2006-03-01' });
const sqs = new aws.SQS({ apiVersion: '2012-11-05' });
const fs = require('fs');


exports.handler = async (event, context) => {
    // 反応したデータの詳細情報を取得する
    const bucket = event.Records[0].s3.bucket.name;
    const key = decodeURIComponent(event.Records[0].s3.object.key.replace(/\+/g, ' '));
    const filename = key.split('/')[key.split('/').length - 1].split('.')[0];
    const taskId = key.split('/')[key.split('/').length - 2].split('_')[1];
    const creator = filename.split('_')[0];

    // JSONファイル用
    const json_key = `digest/info/${creator}/${taskId}.json`;
    const json_params = {
        Bucket: bucket,
        Key: json_key
    };

    // taskIdに相当するJSONファイルをダウンロード
    const uploaded_jsondata = await s3.getObject(json_params)
        .promise()
        .catch((err) => {
            console.log(err);
            const message = `Error getting object ${key} from bucket ${bucket}. Make sure they exist and your bucket is in the same region as this function.`;
            console.log(message);
            throw new Error(message);
        });

    // 取得したJSONファイルをtmpに保存する
    fs.writeFileSync('/tmp/info.json', uploaded_jsondata.Body);

    // JSONファイルを読み込む
    const json_data = JSON.parse(fs.readFileSync('/tmp/info.json', 'utf8'));
    console.log(json_data);


    // inputフォルダ用
    const folder_key = `digest/input/input_${taskId}/`;
    console.log(folder_key);
    const params = {
        Bucket: bucket,
        Prefix: folder_key
    };

    // フォルダ内のファイルを取得する
    const uploaded_data = await s3.listObjects(params)
        .promise()
        .catch((err) => {
            console.log(err);
            const message = `Error getting object ${folder_key} from bucket ${bucket}. Make sure they exist and your bucket is in the same region as this function.`;
            console.log(message);
            throw new Error(message);
        });

    console.log(uploaded_data.Contents);
    console.log(`uploaded_data.Contents.length: ${uploaded_data.Contents.length}`);
    console.log(`json_data.num_clips: ${json_data.num_clips}`);

    // フォルダ内のファイル数とJSONファイルに記しているクリップ数が一致しているかどうか
    if(json_data.num_clips !== uploaded_data.Contents.length){
        console.log("まだクリップは揃っていません.");
        return 'まだクリップは揃っていません';
    }
    console.log("全てのクリップが揃いました.");

    // SQSにタスクIDを入れたメッセージを送る
    var sqs_params = {
        MessageBody: `${creator}/${taskId}`,
        QueueUrl: process.env.SQS_URL,
    }
    console.log(`SQSにメッセージ ${sqs_params.MessageBody} を送信します.`);
    await sqs.sendMessage(sqs_params)
        .promise()
        .catch((err) => {
            console.log(err);
        });

    console.log('完了!');
}