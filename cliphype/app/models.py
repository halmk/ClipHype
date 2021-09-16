from django.db import models
from django.db.models.fields.related import create_many_to_many_intermediary_model
from django.utils import timezone
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialApp


class Digest(models.Model):
    # 作成者 (認証されたユーザか認証されていないユーザ(null))
    creator = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    # 配信者
    streamer = models.CharField(max_length=128)
    # 作成日時
    created = models.DateTimeField(default=timezone.now)
    # ダイジェストのタイトル
    title = models.CharField(max_length=256, blank=True)
    # Celeryによってランダムに生成されるタスクID
    task_id = models.CharField(max_length=256, blank=True, null=True)
    # S3のバケット
    bucket = models.CharField(max_length=128, blank=True)
    # S3に保存される動画へのパス
    video_key = models.CharField(max_length=256, blank=True)
    # ハイライト動画のステータス
    status = models.CharField(max_length=128, blank=True, null=True)
    # クリップの再生時間の合計
    length = models.IntegerField(blank=True, null=True)
    # 使われるクリップのIDをカンマ区切りで並べる
    clips = models.TextField()
    # クリップの数
    num_clips = models.IntegerField(blank=True, null=True)
    # トランジションの種類
    transition = models.CharField(max_length=128, blank=True, null=True)
    # トランジションの長さ
    duration = models.IntegerField(blank=True, null=True)
    # 最初と最後にトランジションをつけるかどうか
    fl_transition = models.BooleanField(blank=True, null=True)


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    content = models.CharField(max_length=1024)
    pub_date = models.DateTimeField(auto_now_add=True)


class SocialAppToken(models.Model):
    app = models.ForeignKey(SocialApp, on_delete=models.CASCADE)
    token = models.TextField()
    token_secret = models.TextField(blank=True)
    expires_at = models.DateTimeField(blank=True, null=True)


class AutoClip(models.Model):
    clip_id = models.CharField(max_length=128)
    url = models.CharField(max_length=128)
    embed_url = models.CharField(max_length=128)
    broadcaster_id = models.CharField(max_length=128)
    broadcaster_name = models.CharField(max_length=128)
    creator_id = models.CharField(max_length=128)
    creator_name = models.CharField(max_length=128)
    created_at = models.CharField(max_length=128)
