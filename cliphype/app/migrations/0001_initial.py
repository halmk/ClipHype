# Generated by Django 3.2.5 on 2021-08-18 20:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialAppToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.TextField()),
                ('token_secret', models.TextField(blank=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socialaccount.socialapp')),
            ],
        ),
        migrations.CreateModel(
            name='Digest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('streamer', models.CharField(max_length=128)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('title', models.CharField(blank=True, max_length=256)),
                ('task_id', models.CharField(blank=True, max_length=256, null=True)),
                ('bucket', models.CharField(blank=True, max_length=128)),
                ('video_key', models.CharField(blank=True, max_length=256)),
                ('status', models.CharField(blank=True, max_length=128, null=True)),
                ('length', models.IntegerField(blank=True, null=True)),
                ('clips', models.TextField()),
                ('num_clips', models.IntegerField(blank=True, null=True)),
                ('transition', models.CharField(blank=True, max_length=128, null=True)),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('content', models.CharField(max_length=1024)),
                ('pub_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
