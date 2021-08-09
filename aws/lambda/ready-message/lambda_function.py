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
RDS_HOST = os.environ('RDS_HOST')
RDS_USER = os.environ('RDS_USER')
RDS_PASSWORD = os.environ('RDS_PASSWORD')
RDS_NAME = os.environ('RDS_NAME')

try:
    conn = pymysql.connect(host=RDS_HOST, user=RDS_USER, passwd=RDS_PASSWORD, db=RDS_NAME, connect_timeout=5)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

def lambda_handler(event, context):

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }