import os
import json
import subprocess
import boto3
import dj_database_url
import pymysql.cursors
import google_api


def connect_to_database():
  database = dj_database_url.parse(os.environ['DATABASE_URL'])
  print(database)
  # Connect to the database
  connection = pymysql.connect(
      host=database['HOST'],
      user=database['USER'],
      password=database['PASSWORD'],
      database=database['NAME'],
      cursorclass=pymysql.cursors.DictCursor
  )
  return connection


def get_credentials(creator):
  credentials = {}
  connection = connect_to_database()
  with connection:
    with connection.cursor() as cursor:
      ## Googleのクライアント情報を取得する
      sql = 'SELECT * FROM `socialaccount_socialapp` WHERE `provider`=%s'
      cursor.execute(sql, ('google',))
      result = cursor.fetchone()
      print(result)
      credentials['client_id'] = result['client_id']
      credentials['client_secret'] = result['secret']
      ## creatorでauth_user.usernameを指定してuser.idを取得する
      sql = 'SELECT * FROM `auth_user` WHERE `username`=%s'
      cursor.execute(sql, (creator,))
      result = cursor.fetchone()
      print(result)
      user_id = result['id']
      ## providerとuser.idでsocialaccount.idを取得する
      sql = 'SELECT * FROM `socialaccount_socialaccount` WHERE `user_id`=%s AND `provider`=%s'
      cursor.execute(sql, (user_id,'google',))
      result = cursor.fetchone()
      print(result)
      id = result['id']
      ## socialaccount.idでsocialtokenを取得する
      sql = 'SELECT * FROM `socialaccount_socialtoken` WHERE `id`=%s'
      cursor.execute(sql, (id,))
      result = cursor.fetchone()
      print(result)
      credentials['access_token'] = result['token']
      credentials['refresh_token'] = result['token_secret']

    connection.commit()

    return credentials


def func():
  # SQSからメッセージを受信する
  ## bucket名は環境変数で取得する
  bucket_name = os.environ['S3_BUCKET']
  sqs_url = os.environ['SQS_URL']
  sqs_client = boto3.client('sqs')
  response = sqs_client.receice_message(
    QueueUrl = sqs_url,
    MaxNumberOfMessages=1,
  )
  message = response.Messages[0].Body
  creator = message.split('_')[0]
  yt_task_id = message.split('_')[1]

  # SQSからメッセージを削除
  response = sqs_client.delete_message(
    QueueUrl = sqs_url,
    ReceiptHandle = response.Messages[0].ReceiptHandle,
  )

  # S3から動画投稿情報を取得する
  s3_client = boto3.client('s3')
  json_key = f'digest/yt_submission_info/{creator}/{yt_task_id}.json'
  response = s3_client.get_object(
      Bucket=bucket_name,
      Key=json_key
  )
  data = response['Body'].read()
  data = data.decode('utf-8')
  youtube_options = json.loads(data)
  task_id = youtube_options['task_id']

  # S3からハイライト動画をダウンロードする
  s3 = boto3.resource('s3')
  bucket = s3.Bucket(bucket_name)

  os.makedirs('/tmp/src/', exist_ok=True)
  video_path = f'/tmp/src/video.mp4'
  video_key = f'digest/output/{creator}/{task_id}.mp4'
  print(f'Downloding clip...: {video_path}, {video_key}')
  bucket.download_file(video_key, video_path)

  # RDSと接続してトークン情報を取得する
  credentials = get_credentials(creator)
  print(credentials)

  # APIを用いて動画をYoutubeにアップロードする
  google_api.uploadVideo(credentials, youtube_options)

  # 自分自身のインスタンスを停止する
  instance_id = subprocess.run(["curl", "http://169.254.169.254/latest/meta-data/instance-id"], capture_output=True)
  instance_id = instance_id.stdout.decode()
  ec2_client = boto3.client('ec2')
  response = ec2_client.terminate_instances(
    InstanceIds = [instance_id],
    DryRun = False
  )


def main():
  print('Hello')

if __name__ == '__main__':
  main()
