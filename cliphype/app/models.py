from django.db import models
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
    # 使われるクリップのIDをカンマ区切りで並べる
    clips = models.TextField()
    # Celeryによってランダムに生成されるタスクID
    task_id = models.CharField(max_length=256, blank=True, null=True)
    # リクエストされた日時 (期限切れなどに使う)
    requested = models.DateTimeField(blank=True, null=True)
    # S3に保存される動画へのパス
    video_key = models.CharField(max_length=256, blank=True)
    # ダイジェストのタイトル
    title = models.CharField(max_length=256, blank=True)


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
