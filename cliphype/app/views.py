import json
import logging
import ast
from django_filters import rest_framework as filters
from rest_framework import viewsets

from allauth.socialaccount.models import SocialAccount
from celery.result import AsyncResult
from django.contrib.auth.models import User
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseServerError, JsonResponse)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django_celery_results.models import TaskResult
from cliphype.settings import S3_BUCKET
from app import aws_api, twitch_api, google_api
from app.models import Contact, Digest, AutoClip
from app.tasks import concat_clips_lambda, upload_highlight_info
from app.serializers import DigestSerializer, TaskResultSerializer, AutoClipSerializer


logger = logging.getLogger(__name__)

'''
トップページ
    フォローしているチャンネルのクリップの表示、ダウンロードができる
'''

def index(request):
    context = {}
    context['bucket_name'] = S3_BUCKET
    user_pk = request.user.pk
    username = request.user.username
    logger.info(f'\nuser: {username}, request.user.pk: {request.user.pk}\n')

    try:
        twitch_account = SocialAccount.objects.get(
            user=user_pk, provider="Twitch")
        logger.info(f'\ntwitch_account: {twitch_account}\n{twitch_account.extra_data}\n')
        extra_data = twitch_account.extra_data
        context['twitch_account'] = extra_data
    except Exception as e:
        logger.warning(f'\nTwitch {e}')

    if request.method == "GET":
        return render(request, 'app/index.html', context)

    # ダイジェスト動画作成リクエスト
    elif request.method == "POST" and request.body:
        response = {}
        response['notes'] = []
        # request.bodyのJSONをDictに変換する
        data = json.loads(request.body)['data']
        if data['creator'] != request.user.username:
            logger.warning(f"\nDifferent user requests a highlight: {request.user.username}, {data['creator']}")

        logger.info(f"\nHighlight is Requested by {data['creator']}.\n{data}\n")

        # タスクを非同期処理で実行する
        task_id = upload_highlight_info.delay(data)

        # Digestテーブルに情報を格納する
        cont = Digest()
        cont.creator = request.user
        cont.streamer = data['streamer']
        cont.title = data['title']
        cont.task_id = task_id
        cont.bucket = S3_BUCKET
        cont.video_key = f"digest/output/{request.user.username}/{task_id}.mp4"
        cont.clips = ','.join([clip['id'] for clip in data['clips']])
        cont.num_clips = data['num_clips']
        cont.length = data['length']
        cont.transition = data['transition']
        cont.duration = data['duration']
        cont.fl_transition = data['fl_transition']
        cont.status = "Requested"
        cont.save()

        result = AsyncResult(task_id)
        logger.info(
            f'\nresult: {result} result.state: {result.state} : {result.ready()}\n'
        )
        response['notes'].append(
            {
                'message': 'Your highlights video successfully requested!! You can check it in the highlights video area below',
                'status':'success'
            }
        )

        return JsonResponse(response)


'''
TwitchAPIを返す
'''


def twitch_api_request(request):
    if request.method == 'GET':
        logger.info(f"\n{request.GET}\n")
        request_dict = request.GET.dict()
        url = request_dict['url']
        params = request_dict['params']
        params = ast.literal_eval(params)
        logger.info(f"\n{url}, {type(params)}\n")
        response = twitch_api.getRequest(url, params)
        #print(response)

        return JsonResponse(response)


'''
HighlightAPIを返す
'''


class DigestViewSet(viewsets.ModelViewSet):
    queryset = Digest.objects.all()
    serializer_class = DigestSerializer
    filter_fields = ['creator', 'streamer']

    def perform_create(self, serializer):
        print(serializer)
        serializer.save()


'''
TaskResultAPIを返す
'''


class TaskResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TaskResult.objects.all()
    serializer_class = TaskResultSerializer
    filter_fields = ['task_id']


'''
AutoClipAPIを返す
'''

class AutoClipFilter(filters.FilterSet):
    broadcaster_name = filters.CharFilter(field_name='broadcaster_name', lookup_expr='contains')
    requested_at_gte = filters.DateTimeFilter(field_name='requested_at', lookup_expr='gte')
    requested_at = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = AutoClip
        fields = ['broadcaster_name', 'requested_at_gte', 'requested_at']


class AutoClipViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AutoClip.objects.all()
    serializer_class = AutoClipSerializer
    filter_class = AutoClipFilter


'''
ダウンロードクリップページ
    クリップをダウンロードする
'''


def download_clip(request):
    clip_id = request.POST['id']
    logger.info(f"\nクリップダウンロードリクエストを受け取りました CLIP ID: {clip_id}")

    clip_file = twitch_api.downloadClip(clip_id, None)

    response = HttpResponse(clip_file['file'], content_type='audio/mp4')
    response['Content-Disposition'] = f'attachment; filename="{clip_file["name"]}"'
    return response


'''
報告フォーム
'''


def report(request):
    context = {}
    context['notes'] = []
    # ユーザが認証されていない場合はログイン画面に遷移させる
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('account_login'))
    try:
        user_pk = request.user.pk
        twitch_account = SocialAccount.objects.get(
            user=user_pk, provider="Twitch")
        logger.info(f'\ntwitch_account: {twitch_account}')
        print(twitch_account.extra_data)
        extra_data = twitch_account.extra_data
        context['twitch_account'] = extra_data
        login_id = extra_data['login']
    except Exception as e:
        logger.warning(f'\nTwitch - {e}')

    if request.method == 'GET':
        return render(request, 'app/report.html', context)
    else:
        user = User.objects.get(username=request.user.username)
        title = request.POST['title']
        content = request.POST['content']
        logger.info(f'user:{user}, title:{title}, content:{content}')
        contact = Contact()
        contact.user = user
        contact.title = title
        contact.content = content
        contact.save()
        context['notes'].append({'message': 'Thank you for the report!!', 'status':'success'})

        return render(request, 'app/report.html', context)


'''
cliphypeの連携解除方法を表示するページ
'''


def unlink(request):
    context = {}
    try:
        user_pk = request.user.pk
        twitch_account = SocialAccount.objects.get(
            user=user_pk, provider="Twitch")
        logger.info(f'\ntwitch_account: {twitch_account}')
        print(twitch_account.extra_data)
        extra_data = twitch_account.extra_data
        context['twitch_account'] = extra_data
        login_id = extra_data['login']

    except Exception as e:
        logger.warning(f'\nTwitch - {e}')

    return render(request, 'app/unlink.html', context)


'''
ポリシーページ
'''

def policy(request):
    return render(request, 'privacy/policy.html')


'''
GoogleAPIのリクエスト結果を返す
'''
def googleAPIRequest(request):
    if request.method == 'GET':
        logger.info(f"\n{request.GET}\n")
        print(request.GET.dict())
        options = {
            "file": "/root/cliphype/cliphype/app/output/test.mp4",
            "keywords": "",
            "title": "ClipHype | Youtube video insert test",
            "description": "test",
            "category": "",
            "privacyStatus": "private",
        }
        response = google_api.uploadVideo(request.user, options)

        return JsonResponse(response)


def googleAPITest(request):
    return render(request, 'app/googleapitest.html')
