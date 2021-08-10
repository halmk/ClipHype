import os
import json
import boto3
import time
import urllib.request
import sys
import logging
import pymysql.cursors


# RDS settings
RDS_HOST = os.environ['RDS_HOST']
RDS_USER = os.environ['RDS_USER']
RDS_PASSWORD = os.environ['RDS_PASSWORD']
RDS_NAME = os.environ['RDS_NAME']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

# Instance settings
SECURITY_GROUP = os.environ['SECURITY_GROUP']
MY_KEY_PAIR = os.environ['MY_KEY_PAIR']
AMI = os.environ['AMI']
INSTANCE_TYPE = os.environ['INSTANCE_TYPE']
MAX_PRICE = os.environ['MAX_PRICE']


def lambda_handler(event, context):
    print(event['Records'][0]['body'])
    # タスクIDを取得
    message = event['Records'][0]['body']
    creator = message.split('/')[0]
    task_id = message.split('/')[1]

    # スポットリクエストを送る
    response = spot_request()

    # リクエストIDを取得
    request_id = response['SpotInstanceRequests'][0]['SpotInstanceRequestId']
    print(request_id)

    with conn.cursor() as cur:
        sql = 'UPDATE `app_digest` SET `status`="Request instance" WHERE `task_id`=%s'
        cur.execute(sql, (task_id))
    conn.commit()

    return "Requested spot instance to create a a highlight video"


# スポットインスタンスリクエスト
def spot_request():
    client = boto3.client('ec2')
    response = client.request_spot_instances(
        InstanceCount=1,
        LaunchSpecification={
            'SecurityGroupIds':[
                SECURITY_GROUP,
            ],
            'KeyName': MY_KEY_PAIR,
            'ImageId': AMI,
            'InstanceType': INSTANCE_TYPE,
        },
        SpotPrice=MAX_PRICE,
        Type='one-time',
    )

    return response


# スポットインスタンスリクエストの詳細を取得
def describe_spot_instance_requests(request_id):
    client = boto3.client('ec2')
    response = client.describe_spot_instance_requests(
        SpotInstanceRequestIds=[
            request_id,
        ],
    )

    return response


# インスタンスの詳細を取得
def describe_instances(instance_id):
    client = boto3.client('ec2')
    response = client.describe_instances(
        InstanceIds=[
            instance_id,
        ],
    )

    return response
