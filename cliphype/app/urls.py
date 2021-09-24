from django.urls import path

from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('highlights', views.DigestViewSet, basename='highlight')
router.register('tasks', views.TaskResultViewSet, basename='task')
router.register('autoclips', views.AutoClipViewSet, basename='autoclip')

urlpatterns = [
    path('', views.index, name='index'),
    path('studio', views.studio, name='studio'),
    path('twitchapi', views.twitch_api_request, name='twitch_api'),
    path('download', views.download_clip, name='download'),
    path('report', views.report, name='report'),
    path('unlink', views.unlink, name='unlink'),
    path('policy', views.policy, name='policy'),
]
