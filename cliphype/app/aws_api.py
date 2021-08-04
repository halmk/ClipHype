import boto3
from cliphype.settings import ACCESS_KEY_ID, SECRET_ACCESS_KEY, S3_BUCKET, REGION_NAME


def get_s3_resource():
    s3 = boto3.resource('s3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=SECRET_ACCESS_KEY,
            region_name=REGION_NAME
    )
    return s3


def get_s3_client():
    s3 = boto3.client('s3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=SECRET_ACCESS_KEY,
            region_name=REGION_NAME
    )
    return s3


def download_file(key, filename):
    s3 = get_s3_resource()
    s3.meta.client.download_file(S3_BUCKET, key, filename)


# filepath で指定されたファイルを key にアップロードする
def upload_file(key, filepath):
    s3 = get_s3_resource()
    s3.meta.client.upload_file(filepath, S3_BUCKET, key)


def list_objects(prefix):
    s3 = get_s3_client()
    response = s3.list_objects(
        Bucket=S3_BUCKET,
        Prefix=prefix,
    )
    return response
