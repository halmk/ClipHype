/*
 input: an uploaded clip
 ( cliphype: digest/src/src_<task_id>/<creator>_<num>.mp4 )

 process: scale video size and fps

 output: upload an scaled video
 ( cliphype: digest/input/input_<task_id>/<creator>_<num>.mp4 )

*/

console.log('Loading function');

const aws = require('aws-sdk');
const s3 = new aws.S3({ apiVersion: '2006-03-01' });
const fs = require('fs');
const execSync = require('child_process').execSync;
process.env.PATH += ':/var/task/bin';


exports.handler = async (event, context) => {
    console.log('Received event:', JSON.stringify(event,));

    // 反応したデータの詳細情報を取得する
    const bucket = event.Records[0].s3.bucket.name;
    const key = decodeURIComponent(event.Records[0].s3.object.key.replace(/\+/g, ' '));
    const extension = key.split('/')[key.split('/').length - 1].split('.')[1];
    const filename = key.split('/')[key.split('/').length - 1].split('.')[0];
    const taskId = key.split('/')[key.split('/').length - 2].split('_')[1];
    const creator = filename.split('_')[0];
    const num = filename.split('_')[1];
    const params = {
        Bucket: bucket,
        Key: key,
    };

    // アップロードされたデータを取得する
    const uploaded_data = await s3.getObject(params)
        .promise()
        .catch((err) => {
            console.log(err);
            const message = `Error getting object ${key} from bucket ${bucket}. Make sure they exist and your bucket is in the same region as this function.`;
            console.log(message);
            throw new Error(message);
        });

    // 取得したファイルをtmpに保存する
    fs.writeFileSync('/tmp/' + filename + '.' + extension, uploaded_data.Body);

    // 動画処理の実行
    const outputFilename = `${creator}_${num}.mp4`;
    execSync('ffmpeg -i /tmp/' + filename + '.' + extension + ' -r 60 -s 1920x1080 /tmp/out_' + outputFilename + ' -y');

    // tmpフォルダに出力エンコード処理結果を取得
    const fileStream = fs.createReadStream('/tmp/out_' + outputFilename);
    fileStream.on('error', function(error) {
        console.log(error);
        throw new Error(error);
    });

    // S3にアップロード
    const outputKey = `digest/input/input_${taskId}/${outputFilename}`;
    await s3.putObject({
            Bucket: bucket,
            Key: outputKey,
            Body: fileStream,
            ContentType: uploaded_data.ContentType,
        })
        .promise()
        .catch((err) => {
            console.log(err);
            const message = `Error getting object ${key} from bucket ${bucket}. Make sure they exist and your bucket is in the same region as this function.`;
            console.log(message);
            throw new Error(message);
        });

    return `Success getting and putting object ${key} from bucket ${bucket}.`;
}
