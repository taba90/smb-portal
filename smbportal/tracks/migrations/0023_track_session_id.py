# Generated by Django 2.0 on 2018-09-03 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracks', '0022_auto_20180903_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='session_id',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='session id'),
        ),
    ]