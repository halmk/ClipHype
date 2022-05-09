from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time
import collections as cl
import json
from . import twitch_api, videos, aws_api


# クリップを繋げるタスク 動画エンコード処理をLambdaで実行する
@shared_task
def concat_clips_lambda(data):
    task_id = concat_clips_lambda.request.id
    print(task_id)
    data['task_id'] = task_id

    num = 1
    for clip in data['clips']:
        clip['num'] = num
        num += 1

    # JSONファイルに書き込み
    json_name = f"{data['creator']}_{task_id}.json"
    json_path = f"{videos.SRC_DIR}{json_name}"
    videos.save_json(json_name, data)

    # JSONファイルをS3にアップロード
    json_key = f"digest/info/{data['creator']}/{task_id}.json"
    print(f"Upload json file: {json_key}")
    aws_api.upload_file(json_key, json_path)

    # ファイルをダウンロード
    files = []
    for clip in data['clips']:
        clip_id = clip['id']
        filename = f"{data['creator']}_{clip['num']:02}.mp4"
        file = twitch_api.downloadClip(clip_id, filename)
        files.append(file)

    # ダウンロードしたファイルをsrcフォルダに格納
    videos.del_files(videos.SRC_DIR)
    print("クリップをsrcフォルダに格納.")
    for file in files:
        videos.save_clip(file)

    # 格納したクリップをS3にアップロードする
    videos.upload_clips(task_id)

@shared_task
def upload_highlight_info(data):
    task_id = upload_highlight_info.request.id
    print(task_id)
    data['task_id'] = task_id

    num = 1
    for clip in data['clips']:
        clip['num'] = num
        num += 1

    # JSONファイルに書き込み
    json_name = f"{data['creator']}_{task_id}.json"
    json_path = f"{videos.SRC_DIR}{json_name}"
    videos.save_json(json_name, data)

    # JSONファイルをS3にアップロード
    json_key = f"digest/info/{data['creator']}/{task_id}.json"
    print(f"Upload json file: {json_key}")
    aws_api.upload_file(json_key, json_path)

@shared_task
def upload_youtube_submission_info(data):
    task_id = upload_youtube_submission_info.request.id
    print(task_id)

    # JSONファイルに書き込み
    json_name = f"{data['creator']}_{task_id}.json"
    json_path = f"{videos.SRC_DIR}{json_name}"
    videos.save_json(json_name, data)

    # JSONファイルをS3にアップロード
    json_key = f"digest/yt_submission_info/{data['creator']}/{task_id}.json"
    print(f"Upload json file: {json_key}")
    aws_api.upload_file(json_key, json_path)
