# Generated by Django 2.0 on 2018-08-06 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0018_auto_20180718_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bike',
            name='nickname',
            field=models.CharField(max_length=100, verbose_name='bikename'),
        ),
    ]
