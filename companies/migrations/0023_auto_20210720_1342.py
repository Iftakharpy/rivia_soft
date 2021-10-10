# Generated by Django 3.2.2 on 2021-07-20 07:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0022_auto_20210718_0004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='limitedvattracker',
            name='HMRC_deadline',
            field=models.DateField(blank=True, null=True, verbose_name='HMRC Deadline'),
        ),
        migrations.AlterField(
            model_name='limitedvattracker',
            name='period_end',
            field=models.DateField(null=True, verbose_name='Period End'),
        ),
        migrations.AlterField(
            model_name='limitedvattracker',
            name='period_start',
            field=models.DateField(null=True, verbose_name='Period Start'),
        ),
        migrations.CreateModel(
            name='LimitedConfirmationStatementTracker',
            fields=[
                ('statement_id', models.AutoField(db_index=True, editable=False, primary_key=True, serialize=False, verbose_name='Statement ID')),
                ('HMRC_deadline', models.DateField(null=True, verbose_name='HMRC Deadline')),
                ('is_submitted', models.BooleanField(default=False, verbose_name='Is Submitted')),
                ('submitted_by', models.TextField(blank=True, default='', null=True, verbose_name='Submitted By')),
                ('submission_date', models.DateField(blank=True, null=True, verbose_name='Submission Date')),
                ('is_documents_uploaded', models.BooleanField(default=False, verbose_name='Is Documents Uploaded')),
                ('remarks', models.TextField(blank=True, null=True, verbose_name='Remarks')),
                ('last_updated_on', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Last Updated On')),
                ('client_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='limited_confirmation_client_id', to='companies.limited', verbose_name='Client ID')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='limited_confirmation_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
            ],
            options={
                'verbose_name': 'Limited Confirmation Statement',
                'verbose_name_plural': 'Limited Confirmation Statements',
            },
        ),
    ]