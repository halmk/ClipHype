from rest_framework import serializers

from app.models import Digest
from django_celery_results.models import TaskResult


class DigestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Digest
        fields = ['creator', 'streamer', 'created', 'clips', 'task_id', 'bucket', 'video_key', 'title', 'status']


class TaskResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskResult
        fields = ['task_id', 'task_name', 'status']
