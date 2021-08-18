import os
import json
import boto3
import time
import sys
import logging
import ffmpeg

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event['Records'][0]['s3']['object']['key'])

    # get parameters from s3 object key triggered
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    filename = key.split('/')[-1]
    creator = filename.split('_')[0]
    num = filename.split('_')[1].split('.')[0]
    num = str(int(num))
    task_id = key.split('_')[1].split('/')[0]
    logger.info(task_id)

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    s3_client = boto3.client('s3')
    json_key = f'digest/info/{creator}/{task_id}.json'
    response = s3_client.get_object(
        Bucket=bucket_name,
        Key=json_key
    )
    data = response['Body'].read()
    data = data.decode('utf-8')
    data = json.loads(data)
    logger.info(data)

    # download the triggered clip
    os.makedirs('/tmp/src/', exist_ok=True)
    os.makedirs('/tmp/out/', exist_ok=True)
    clip_path = f'/tmp/src/{filename}'

    logger.info(f'Downloding clip...: {clip_path}, {key}')
    bucket.download_file(key, clip_path)

    # process draw-text to the clip
    out_path = f'/tmp/out/{filename}'

    title = ""
    for clip in data['clips']:
        if clip['num'] == num:
            title = clip['title']
            break

    fontsize = data['fontsize']
    fontcolor = data['fontcolor']
    borderw = data['borderw']
    position = data['position']

    p_y = position.split('-')[0]
    p_x = position.split('-')[1]
    x = "0" if p_x == "left" else "w-tw"
    y = "0" if p_y == "top" else "h-th"

    stream = ffmpeg.input(clip_path)
    stream_audio = stream.audio
    stream = ffmpeg.drawtext(stream,
        text=title,
        fontsize=fontsize,
        fontcolor=fontcolor,
        borderw=borderw,
        x=x,
        y=y,
        fix_bounds=True
    )
    stream = ffmpeg.output(stream, stream_audio, out_path)
    stream.run()

    # upload the processed clip
    out_key = f'digest/input/input_{task_id}/{filename}'
    logger.info(f'Uploading scaled clip...: {out_path}, {out_key}')
    bucket.upload_file(out_path, out_key)

    return {
        'statusCode': 200,
        'body': json.dumps('Draw-text clip. ')
    }
