import os
import json
import boto3
import time
import urllib.request
import sys
import logging
import pymysql.cursors


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Instance settings
SECURITY_GROUP1 = os.environ['SECURITY_GROUP1']
SECURITY_GROUP2 = os.environ['SECURITY_GROUP2']
VOLUME_SIZE = int(os.environ['VOLUME_SIZE'])
MY_KEY_PAIR = os.environ['MY_KEY_PAIR']
AMI = os.environ['AMI']
INSTANCE_TYPE = os.environ['INSTANCE_TYPE']
MAX_PRICE = os.environ['MAX_PRICE']
SNAPSHOT_ID = os.environ['SNAPSHOT_ID']


def lambda_handler(event, context):
    print(event['Records'][0]['body'])
    # タスクIDを取得
    message = event['Records'][0]['body']
    creator = message.split('/')[0]
    task_id = message.split('/')[1]

    # スポットリクエストを送る
    response = spot_request()

    return "Requested spot instance to create a a highlight video"


# スポットインスタンスリクエスト
def spot_request():
    client = boto3.client('ec2')
    response = client.request_spot_instances(
        InstanceCount=1,
        LaunchSpecification={
            'SecurityGroupIds':[
                SECURITY_GROUP1,
                SECURITY_GROUP2
            ],
            'BlockDeviceMappings': [
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'SnapshotId': SNAPSHOT_ID,
                        'VolumeSize': VOLUME_SIZE,
                        'VolumeType': 'gp2',
                        'Encrypted': False
                    }
                }
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
