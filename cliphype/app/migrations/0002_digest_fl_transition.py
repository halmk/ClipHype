# Generated by Django 3.2.5 on 2021-08-22 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='digest',
            name='fl_transition',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
