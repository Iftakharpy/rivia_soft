# Generated by Django 3.2.9 on 2021-12-08 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_logs', '0003_alter_userloginhistory_logged_out_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userloginhistory',
            name='logged_out_at',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
