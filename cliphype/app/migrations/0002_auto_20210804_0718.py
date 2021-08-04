# Generated by Django 3.2.5 on 2021-08-04 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='digest',
            name='requested',
        ),
        migrations.AddField(
            model_name='digest',
            name='duration',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='digest',
            name='length',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='digest',
            name='num_clips',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='digest',
            name='status',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='digest',
            name='transition',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
