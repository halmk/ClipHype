import os
import json
import boto3
import time
import urllib.request
import sys
import logging
import pymysql


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
        connect_timeout=5
    )
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

def lambda_handler(event, context):
    key = event['Records'][0]['s3']['object']['key']
    task_id = key.split('_')[1].split('/')[0]
    creator = key.split('/')[-1].split('_')[0]
    logger.info(f'{creator}, {task_id}')

    with conn.cursor() as cur:
        sql = 'SELECT `bucket`, `num_clips` FROM `app_digest` WHERE `task_id`=%s'
        cur.execute(sql, (task_id))
        task = cur.fetchone()
        logger.info(task)

    s3_client = boto3.client('s3')
    input_prefix = f'digest/input/input_{task_id}/'
    response = s3_client.list_objects(
        Bucket=task['bucket'],
        Prefix=input_prefix
    )
    num_scaled_clips = len(response['Contents'])

    logger.info(f'current:{num_scaled_clips}, total:{task["num_clips"]}')
    if task['num_clips'] != num_scaled_clips:
        return "clips are scaled yet."

    sqs_client = boto3.client('sqs')
    response = sqs_client.send_message(
        QueueUrl=os.environ['SQS_URL'],
        MessageBody=f'{creator}/{task_id}'
    )

    status = 'Ready to request instance'
    with conn.cursor() as cur:
        sql = 'UPDATE app_digest SET `status`=%s WHERE `task_id`=%s'
        cur.execute(sql, (status, task_id))

    conn.commit()

    return {
        'statusCode': 200,
        'body': json.dumps('Send ready message to SQS.')
    }