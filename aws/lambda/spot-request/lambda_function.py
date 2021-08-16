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


def lambda_handler(event, context):
    print(event['Records'][0]['body'])
    message = event['Records'][0]['body']
    bucket_name = message.split('/')[0]
    creator = message.split('/')[1]
    task_id = message.split('/')[2]

    # download info json file from s3 corresponding to the received message
    s3_client = boto3.client('s3')
    info_key = f'digest/info/{task_id}.json'
    response = s3_client.get_object(
        Bucket=bucket,
        Key=info_key
    )
    params = response['Body'].read()
    params = params.decode('utf-8')
    params = json.loads(params)
    # update the status in params
    params['status'] = 'Request instance'

    info_path = '/tmp/info.json'
    with open(info_path, 'w') as f:
        json.dump(params,f,indent=4)

    # upload (overwrite) the updated json file
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.upload_file(info_path, info_key)

    # send a spot request
    response = spot_request()

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
