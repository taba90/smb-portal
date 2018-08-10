# Generated by Django 2.0 on 2018-08-09 14:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracks', '0013_auto_20180809_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cost',
            name='segment',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tracks.Segment', verbose_name='segment'),
        ),
        migrations.AlterField(
            model_name='health',
            name='segment',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tracks.Segment', verbose_name='segment'),
        ),
    ]
