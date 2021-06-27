# Generated by Django 3.2.2 on 2021-06-27 12:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0012_alter_limited_client_file_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='LimitedTracker',
            fields=[
                ('tracker_id', models.AutoField(db_index=True, primary_key=True, serialize=False, verbose_name='Tracker ID')),
                ('creation_date', models.DateTimeField(blank=True, default=django.utils.timezone.localtime, editable=False, null=True, verbose_name='Creation Datetime')),
                ('job_description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('remarks', models.TextField(blank=True, default='', null=True, verbose_name='Remarks')),
                ('has_issue', models.BooleanField(default=False, verbose_name='Has Issue')),
                ('deadline', models.DateField(default=django.utils.timezone.localtime, null=True, verbose_name='Deadline')),
                ('is_completed', models.BooleanField(blank=True, default=False, verbose_name='Completed')),
                ('complete_date', models.DateField(blank=True, null=True, verbose_name='Complete Date')),
                ('new_customer', models.BooleanField(blank=True, default=False, editable=False, null=True, verbose_name='New customer')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='limited_tracker_assigned_to', to=settings.AUTH_USER_MODEL, verbose_name='Assigned to')),
                ('client_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='limited_tracker_client_id', to='companies.limited', verbose_name='Client ID')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='limited_tracker_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('done_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='limited_tracker_done_by', to=settings.AUTH_USER_MODEL, verbose_name='Done By')),
                ('issue_created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='limited_tracker_issue_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Issue Created By')),
            ],
            options={
                'verbose_name': 'Limited Tracker',
                'verbose_name_plural': 'Limited Trackers',
            },
        ),
    ]
