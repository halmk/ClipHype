import os
import json
import boto3
import time
import urllib.request
import sys
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

SQS_URL = os.environ['SQS_URL']


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    task_id = key.split('_')[1].split('/')[0]
    creator = key.split('/')[-1].split('_')[0]
    logger.info(f'{creator}, {task_id}')

    s3_client = boto3.client('s3')
    # get the number of clips has to be processed
    info_key = f'digest/info/{task_id}.json'
    response = s3_client.get_object(
        Bucket=bucket,
        Key=info_key
    )
    params = response['Body'].read()
    params = params.decode('utf-8')
    params = json.loads(params)
    logger.info(params)
    num_clips = params['num_clips']

    # get the number of processed input clips
    input_prefix = f'digest/input/input_{task_id}/'
    response = s3_client.list_objects(
        Bucket=bucket,
        Prefix=input_prefix
    )
    num_processed_clips = len(response['Contents'])

    # compare the number of clips has to be and processed
    logger.info(f'current:{num_processed_clips}, total:{num_clips}')
    if num_clips != num_processed_clips:
        return "clips are scaled yet."

    sqs_client = boto3.client('sqs')
    response = sqs_client.send_message(
        QueueUrl=SQS_URL,
        MessageBody=f'{bucket}/{creator}/{task_id}'
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Send ready message to SQS.')
    }
