# 動画編集についてのモジュール

import os
import subprocess
import shutil
import sys
import json
from .aws_api import upload_file
from .models import Digest


LIST_PATH = 'list.txt'
SRC_DIR = 'app/src/'
INPUT_DIR = 'app/input/'
OUTPUT_DIR = 'app/output/'
OUTPUT_PATH = 'app/output/out.mp4'
TBN = '15360'

fps = 60
width = 1920

os.makedirs(SRC_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ファイルをsrcフォルダに保存する
def save_clip(file):
    print(f"実行ファイルのパス: {os.getcwd()}")
    path = SRC_DIR + file['name']
    file = file['file']

    if file.status_code == 200:
        with open(path, mode='wb') as f:
            file.raw.decode_content = True
            shutil.copyfileobj(file.raw, f)


def save_json(filename, data):
    path = SRC_DIR + filename
    with open(path, 'w') as f:
        json.dump(data,f,indent=4)


# 入力ファイルを取得します
def get_input_files():
    files = os.listdir(INPUT_DIR)
    res = []
    for file in files:
        if file.endswith('.mp4'):
            res.append(file)
    return res


# 変換前の入力ファイル名を取得します
def get_source_files():
    files = os.listdir(SRC_DIR)
    res = []
    for file in files:
        if file.endswith('.mp4'):
            res.append(file)
    return res


# ffmpeg concatコマンドのための入力ファイルリストを作成します
def create_list():
    files = get_input_files()

    with open(LIST_PATH, mode='w') as f:
        for file in files:
            path = f"{INPUT_DIR}{file}"
            f.write(f"file '{path}'\n")


# 動画の解像度とFPSを合わせて input フォルダに格納
def conv_files():
    files = get_source_files()

    index = 1
    for file in files:
        path = SRC_DIR + file
        output = f"{INPUT_DIR}input{index:02}.mp4"
        index += 1

        cmd = f'ffmpeg -y -i file:{path} -r {int(fps)} -s {int(width)}x{int(width*9/16)} {output}'
        subprocess.check_call(cmd.split())
        #os.remove(path)


# ファイルのタイムスケールを変換し、INPUT_DIRへ出力します
def scale_time_files():
    files = get_source_files()

    for file in files:
        path = SRC_DIR + file
        output = INPUT_DIR + file
        cmd = f"ffmpeg -y -i {path} -c copy -video_track_timescale {TBN} {output}"

        subprocess.check_call(cmd.split(), shell=False)


# 入力ファイルに concat demxuer を適用して1つの動画にまとめる
def concat_demxuer():
    cmd = f'ffmpeg -f concat -safe 0 -i {LIST_PATH} -c copy {OUTPUT_PATH}'
    subprocess.check_call(cmd.split(), shell=False)


# 入力フォルダ内のファイルに concat filter を適用する
def concat_filter():
    files = get_input_files()
    cmd = "ffmpeg -y "
    num = len(files)

    for file in files:
        file_path = f"{INPUT_DIR}{file}"
        cmd += f"-i file:{file_path} "

    cmd += f'-filter_complex "concat=n={num}:v=1:a=1" {OUTPUT_PATH}'
    print(f"コマンド: {cmd}")
    #subprocess.check_call(cmd.split())
    os.system(cmd)


# 指定されたディレクトリ内にあるファイルを全て削除する
def del_files(path):
    # pathのディレクトリ内のファイルを取得
    files = os.listdir(path)
    for file in files:
        file_path = path + file
        os.remove(file_path)


# データベースからvideo_keyを取得してS3にアップロードする
def upload_output(task_id):
    digest = Digest.objects.get(task_id=task_id)
    print(digest)
    upload_file(digest.video_key, OUTPUT_PATH)


# S3の digest/src_{task_id}/{filename} にsrcに格納されている全てのmp4ファイルをアップロードする
def upload_clips(task_id):
    files = get_source_files()
    for file in files:
        key = f'digest/src/src_{task_id}/{file}'
        filepath = f'{SRC_DIR}{file}'
        upload_file(key, filepath)
