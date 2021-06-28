# Generated by Django 3.2.2 on 2021-06-28 00:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0014_auto_20210628_0655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='limitedsubmissiondeadlinetracker',
            name='is_documents_uploaded',
            field=models.BooleanField(default=False, null=True, verbose_name='Is Documents Uploaded'),
        ),
        migrations.AlterField(
            model_name='limitedsubmissiondeadlinetracker',
            name='is_submitted',
            field=models.BooleanField(default=False, null=True, verbose_name='Is Submitted'),
        ),
        migrations.AlterField(
            model_name='limitedsubmissiondeadlinetracker',
            name='last_updated_on',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Last Updated On'),
        ),
        migrations.AlterField(
            model_name='limitedsubmissiondeadlinetracker',
            name='submission_date',
            field=models.DateField(blank=True, null=True, verbose_name='Submission Date'),
        ),
        migrations.AlterField(
            model_name='limitedsubmissiondeadlinetracker',
            name='submitted_by',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Submitted By'),
        ),
    ]