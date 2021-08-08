import os
import json
import boto3
import time
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
    conn = pymysql.connect(host=RDS_HOST, user=RDS_USER, passwd=RDS_PASSWORD, db=RDS_NAME, connect_timeout=2)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")


def lambda_handler(event, context):
    # TODO implement
    logger.info(event['Records'][0]['s3']['object']['key'])
    key = event['Records'][0]['s3']['object']['key']
    task_id = key.split('_')[1].split('.')[0]
    logger.info(task_id)

    with conn.cursor() as cur:
        sql = 'SELECT * FROM `app_digest` WHERE `task_id`=%s'
        cur.execute(sql, (task_id,))
        result = cur.fetchone()
        print(result)



    client = boto3.client('s3')
    response = client.get_object(
        Bucket=task.bucket,
        Key=key
    )
    body = response['Body'].read()

    with open('clip.mp4', 'wb') as f:
        f.write(body)



    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
