""" This is for TwitchAPI """
from datetime import datetime
import time
import requests
import json
import logging

from app.models import SocialAppToken
from allauth.socialaccount.models import SocialApp

logger = logging.getLogger(__name__)


def getToken():
    Twitch = SocialApp.objects.all().filter(provider="Twitch").first()
    params = {
        'client_id': Twitch.client_id,
        'client_secret': Twitch.secret,
        'grant_type': 'client_credentials'
    }
    res = requests.post('https://id.twitch.tv/oauth2/token', params=params)
    logger.debug(f'\n{res}\n')
    token = json.loads(res.text)['access_token']
    return token


def getRequest(url, params, count=0):
    Twitch = SocialApp.objects.all().filter(provider="Twitch").first()
    try:
        twitch_token = SocialAppToken.objects.get(app=Twitch)
    except SocialAppToken.DoesNotExist as e:
        logger.debug(e)
        token = getToken()
        twitch_token = SocialAppToken.objects.create(app=Twitch, token=token)

    logger.debug(f'\n{twitch_token.token}\n')
    headers = {
        'Client-ID': Twitch.client_id,
        'Authorization': f'Bearer {twitch_token.token}'
    }
    response = requests.get(url, headers=headers, params=params)
    logger.debug(f'\n{response}\n')
    if response.status_code != 200:
        if count > 0:
            time.sleep(3)
        if count > 1:
            raise Exception
        twitch_token.token = getToken()
        twitch_token.save()
        return getRequest(url, params, count+1)
    else:
        logger.info(f"\nRate-limit: Remaining:{response.headers.get('Ratelimit-Remaining')}, Reset:{response.headers.get('Ratelimit-Reset')}\n")
        response_json = response.json()
        return response_json


# Get Clips APIを使用する. クリップの情報を返す(JSON)
# https://dev.twitch.tv/docs/api/reference/#get-clips
def getClip(clipId):
    params = {
        "id": clipId,
    }
    return getRequest('https://api.twitch.tv/helix/clips', params)


# Get Videos API を使用する. 指定されたビデオIDの情報を返す
def getVideo(videoId):
    params = (
        ('id', videoId),
    )
    return getRequest('https://api.twitch.tv/helix/videos', params)


# CLIP_DIRに指定されたIDのクリップのmp4ファイルをダウンロードする
def downloadClip(clipID, filename):
    clipData = getClip(clipID)

    logger.info(f"取得したクリップの内容：{clipID},{filename}")
    thumbnail_url = clipData["data"][0]["thumbnail_url"].split('/')[3]
    key = thumbnail_url.split('-preview-')[0]

    clip_file = {}
    if filename is None:
        clip_file['name'] = clipData['data'][0]['created_at'] + '_' + clipData['data'][0]['id'] + '.mp4'
    else:
        clip_file['name'] = filename

    clip_file_url = "https://clips-media-assets2.twitch.tv/" + key + ".mp4"

    logger.info(f"クリップのダウンロードを開始します :{clip_file_url}")
    clip_file['file'] = requests.get(clip_file_url, stream=True)

    if clip_file['file'].status_code == 200:
        logger.info("ダウンロードに成功しました")
        return clip_file
    else:
        logger.warning(f"ダウンロードに失敗しました: {clip_file['file'].status_code}")
        return False


if __name__ == "__main__":
    #print(downloadClip('CrowdedSpeedyPheasantPastaThat-YhiNhmatsMe0fwuz', ''))
    params_test = {"broadcaster_id":"91009387","started_at":"2021-07-16T00:00:00Z","ended_at":"2021-07-23T00:00:00Z","first":27}
    print(getRequest("https://api.twitch.tv/helix/clips", params_test))
