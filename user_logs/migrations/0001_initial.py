# Generated by Django 5.1.4 on 2025-01-01 04:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FailedLoginAttempts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(verbose_name='Public ip address of device')),
                ('credentials', models.TextField()),
                ('device_user_agent', models.TextField(verbose_name='User Agent')),
                ('tried_to_log_in_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Failed User Login History',
                'verbose_name_plural': 'Failed User Login Histories',
            },
        ),
        migrations.CreateModel(
            name='UserLoginHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(verbose_name='Public ip address of device')),
                ('device_user_agent', models.TextField(verbose_name='User Agent')),
                ('logged_in_at', models.DateTimeField(auto_now_add=True)),
                ('last_seen_at', models.DateTimeField(auto_now=True)),
                ('logged_out_at', models.DateTimeField(default=None, null=True)),
            ],
            options={
                'verbose_name': 'User Login History',
                'verbose_name_plural': 'User Login Histories',
            },
        ),
        migrations.CreateModel(
            name='ActiveUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_seen_at', models.DateTimeField(auto_now=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sessions.session')),
            ],
            options={
                'verbose_name': 'Active User',
                'verbose_name_plural': 'Active Users',
            },
        ),
    ]
