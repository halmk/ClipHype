import os
import json
import boto3
import time
import urllib.request


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

    # インスタンスが running になるまで待機
    is_pending = True
    total = 0
    while is_pending:
        # 5秒毎にインスタンスの状態を取得する
        time.sleep(5)
        total += 5
        print(f'current total: {total}seconds')
        try:
            request_data = describe_spot_instance_requests(request_id)
            instance_id = request_data['SpotInstanceRequests'][0]['InstanceId']
            print(instance_id)
            instance_data = describe_instances(instance_id)
            print(instance_data['Reservations'][0]['Instances'][0]['State']['Name'])
            # running になったら isPending を False にする
            if instance_data['Reservations'][0]['Instances'][0]['State']['Name'] == 'running':
                print(instance_data)
                ip_address = instance_data['Reservations'][0]['Instances'][0]['PublicIpAddress']
                is_pending = False
        except Exception as e:
            print(e)

        if total >= 30:
            break

    print(f'total: about {total}seconds')

    # JSONデータの取得
    print("JSONファイルを取得します.")
    json_key = f'digest/info/{creator}/{task_id}.json'
    json_path = f'/tmp/{creator}_{task_id}.json'
    download_file(json_key, json_path)

    # ちょっと一時停止
    time.sleep(5)

    json_file = open(json_path, 'r')
    json_data = json.load(json_file)

    # インスタンスに送るデータの準備
    print("起動したインスタンスにPOST")
    instance_url = f'http://{ip_address}:3000/'
    print(f'インスタンスのURL: {instance_url}')
    data = {
        'data': json_data,
        'request_id': request_id,
        'instance_id': instance_id,
    }
    headers = {
        'Content-Type': 'application/json',
    }

    # 起動したインスタンスにPOST 成功か失敗かは分からない
    req = urllib.request.Request(instance_url, json.dumps(data).encode(), headers)
    count = 0
    while count < 8:
        count += 1
        print(f'{count}回目のPOSTリクエスト')
        try:
            res = urllib.request.urlopen(req)
            print(res.read())
        except Exception as e:
            print(e)
        else:
            break
        time.sleep(10)



# スポットインスタンスリクエスト
def spot_request():
    client = boto3.client('ec2')
    response = client.request_spot_instances(
        InstanceCount=1,
        LaunchSpecification={
            'SecurityGroupIds':[
                os.environ['SECURITY_GROUP'],
            ],
            'KeyName': os.environ['MY_KEY_PAIR'],
            'ImageId': os.environ['AMI'],
            'InstanceType': os.environ['INSTANCE_TYPE'],
        },
        SpotPrice=os.environ['MAX_PRICE'],
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


# S3からファイルをダウンロード
def download_file(key, filename):
    s3 = boto3.resource('s3')
    s3.meta.client.download_file('cliphype', key, filename)
