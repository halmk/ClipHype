import os
import json
import requests
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
    creator = key.split('/')[-2]
    filename = key.split('/')[-1]
    task_id = filename.split('.')[0]
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

    os.makedirs('/tmp/clip/', exist_ok=True)

    # download clips from Twitch
    for clip in data["clips"]:
        thumbnail_url = clip["thumbnail_url"].split('/')[3]
        key = thumbnail_url.split('-preview-')[0]
        url = "https://clips-media-assets2.twitch.tv/" + key + ".mp4"
        logger.info(f"クリップのダウンロードを開始します :{url}")
        response = requests.get(url)
        clip_filename = f"{creator}_{clip['num']:02}.mp4"
        save_filepath = f"/tmp/clip/{clip_filename}"
        with open(save_filepath, 'wb') as f:
            f.write(response.content)

        # upload the downloaded clip to S3
        out_key = f'digest/src/src_{task_id}/{clip_filename}'
        logger.info(f'Uploading the downloaded clip...: {save_filepath}, {out_key}')
        bucket.upload_file(save_filepath, out_key)

        # remove the downloaded clip from disk
        os.remove(save_filepath)


    return {
        'statusCode': 200,
        'body': json.dumps('Scaled clip. ')
    }
