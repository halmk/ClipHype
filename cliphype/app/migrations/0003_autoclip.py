# Generated by Django 3.2.5 on 2021-09-15 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_digest_fl_transition'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutoClip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clip_id', models.CharField(max_length=128)),
                ('url', models.CharField(max_length=128)),
                ('embed_url', models.CharField(max_length=128)),
                ('broadcaster_id', models.CharField(max_length=128)),
                ('broadcaster_name', models.CharField(max_length=128)),
                ('creator_id', models.CharField(max_length=128)),
                ('creator_name', models.CharField(max_length=128)),
                ('created_at', models.CharField(max_length=128)),
            ],
        ),
    ]
