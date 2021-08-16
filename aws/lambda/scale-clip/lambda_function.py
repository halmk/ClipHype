import os
import json
import boto3
import time
import sys
import logging
import subprocess


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event['Records'][0]['s3']['object']['key'])

    # get parameters from s3 object key triggered
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    filename = key.split('/')[-1]
    creator = filename.split('_')[0]
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

    # process scale to the clip
    out_path = f'/tmp/out/{filename}'
    scale_args = ['ffmpeg', '-i', clip_path, '-r', '60', '-s', '1920x1080', out_path, '-y']
    logger.info(f'Scaling clip...')
    res = subprocess.call(scale_args)

    # upload the processed clip
    if data['is_drawtext']:
        out_key = f'digest/scaled/scaled_{task_id}/{filename}'
    else:
        out_key = f'digest/input/input_{task_id}/{filename}'

    logger.info(f'Uploading scaled clip...: {out_path}, {out_key}')
    bucket.upload_file(out_path, out_key)

    return {
        'statusCode': 200,
        'body': json.dumps('Scaled clip. ')
    }
