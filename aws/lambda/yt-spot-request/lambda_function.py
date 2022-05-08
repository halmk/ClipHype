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
    # get parameters from s3 object key triggered
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    creator = key.split('/')[-2]
    filename = key.split('/')[-1]
    yt_task_id = filename.split('.')[0]
    logger.info(yt_task_id)

    s3_client = boto3.client('s3')
    json_key = f'digest/yt_submission_info/{creator}/{yt_task_id}.json'
    response = s3_client.get_object(
        Bucket=bucket_name,
        Key=json_key
    )
    data = response['Body'].read()
    data = data.decode('utf-8')
    data = json.loads(data)
    logger.info(data)
    task_id = data['task_id']

    # send a spot request
    response = spot_request()

    # send a ready message to sqs
    sqs_client = boto3.client('sqs')
    response = sqs_client.send_message(
        QueueUrl=SQS_URL,
        MessageBody=f'{creator}_{task_id}'
    )

    return "Requested spot instance to submit a highlight video for Youtube."


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
