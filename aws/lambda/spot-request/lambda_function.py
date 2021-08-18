import os
import json
import boto3
import time
import urllib.request
import sys
import logging


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

SQS_URL = os.environ['SQS_URL']


def lambda_handler(event, context):
    print(event['Records'][0]['body'])
    message = event['Records'][0]['body']
    bucket_name = message.split('/')[0]
    creator = message.split('/')[1]
    task_id = message.split('/')[2]

    # send a spot request
    response = spot_request()

    # send a ready message to sqs
    sqs_client = boto3.client('sqs')
    response = sqs_client.send_message(
        QueueUrl=SQS_URL,
        MessageBody=f'{task_id}'
    )

    return "Requested spot instance to create a a highlight video"


# spot instance request
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
