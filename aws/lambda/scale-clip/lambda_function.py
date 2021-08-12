import os
import json
import boto3
import time
import sys
import logging
import pymysql.cursors
import subprocess


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# RDS settings
RDS_HOST = os.environ['RDS_HOST']
RDS_USER = os.environ['RDS_USER']
RDS_PASSWORD = os.environ['RDS_PASSWORD']
RDS_NAME = os.environ['RDS_NAME']

try:
    conn = pymysql.connect(
        host=RDS_HOST,
        user=RDS_USER,
        passwd=RDS_PASSWORD,
        db=RDS_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
    )
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")


def lambda_handler(event, context):
    logger.info(event['Records'][0]['s3']['object']['key'])
    key = event['Records'][0]['s3']['object']['key']
    filename = key.split('/')[-1]
    task_id = key.split('_')[1].split('/')[0]
    logger.info(task_id)

    with conn.cursor() as cur:
        sql = 'SELECT `bucket`, `status`, `num_clips` FROM `app_digest` WHERE `task_id`=%s'
        cur.execute(sql, (task_id))
        task = cur.fetchone()
        logger.info(task)

    os.makedirs('/tmp/src/', exist_ok=True)
    os.makedirs('/tmp/out/', exist_ok=True)
    clip_path = f'/tmp/src/{filename}'

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(task['bucket'])
    logger.info(f'Downloding clip...: {clip_path}, {key}')
    bucket.download_file(key, clip_path)

    out_path = f'/tmp/out/{filename}'
    scale_args = ['ffmpeg', '-i', clip_path, '-r', '60', '-s', '1920x1080', out_path, '-y']
    logger.info(f'Scaling clip...')
    res = subprocess.call(scale_args)

    out_key = f'digest/input/input_{task_id}/{filename}'
    logger.info(f'Uploading scaled clip...: {out_path}, {out_key}')
    bucket.upload_file(out_path, out_key)

    input_prefix = f'digest/input/input_{task_id}/'
    client = boto3.client('s3')
    logger.info(f'List scaled clip: {task["bucket"]}, {input_prefix}')
    scaled_objects = client.list_objects(
        Bucket=task['bucket'],
        Prefix=input_prefix
    )
    logger.info(scaled_objects)
    num_scaled_clips = len(scaled_objects['Contents'])

    status = f'Scaling clips {num_scaled_clips}/{task["num_clips"]}'
    if num_scaled_clips == task["num_clips"]:
        status = 'Request instance'

    logger.info(f'Update task status: {status}')
    with conn.cursor() as cur:
        sql = 'UPDATE `app_digest` SET `status`=%s WHERE `task_id`=%s'
        cur.execute(sql, (status, task_id))

    conn.commit()

    return {
        'statusCode': 200,
        'body': json.dumps('Scaled clip. ')
    }
