# Generated by Django 5.1.4 on 2025-02-21 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_logs', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='failedloginattempts',
            name='extra_info',
            field=models.TextField(default='', verbose_name='Extra Info'),
        ),
        migrations.AlterField(
            model_name='failedloginattempts',
            name='credentials',
            field=models.TextField(default='', verbose_name='Credentials'),
        ),
        migrations.AlterField(
            model_name='failedloginattempts',
            name='device_user_agent',
            field=models.TextField(default='', verbose_name='User Agent'),
        ),
    ]
