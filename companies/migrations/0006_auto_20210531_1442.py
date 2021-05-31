# Generated by Django 3.2.2 on 2021-05-31 08:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0005_alter_selfassesment_date_of_birth'),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('issue_id', models.AutoField(db_index=True, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Issue Id')),
                ('description', models.TextField(db_index=True, default='New Issue', max_length=255, verbose_name='Type Name')),
            ],
            options={
                'verbose_name': 'Issue',
                'verbose_name_plural': 'Issues',
            },
        ),
        migrations.AddField(
            model_name='selfassesmenttracker',
            name='has_issue',
            field=models.BooleanField(default=False, verbose_name='Has Issue'),
        ),
        migrations.AddField(
            model_name='selfassesmenttracker',
            name='issue_created_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='selfassesment_tracker_issue_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Issue Created By'),
        ),
        migrations.AddField(
            model_name='selfassesmenttracker',
            name='remarks',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Remarks'),
        ),
        migrations.AlterField(
            model_name='selfassesment',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True, verbose_name='Date of Birth'),
        ),
        migrations.AlterField(
            model_name='selfassesmenttracker',
            name='is_completed',
            field=models.BooleanField(blank=True, default=False, verbose_name='Completed'),
        ),
        migrations.CreateModel(
            name='TrackerHasIssues',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='TrackerHasIssues_issue_id', to='companies.issue', verbose_name='Tracker Id')),
                ('tracker_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='TrackerHasIssues_tracker_id', to='companies.selfassesmenttracker', verbose_name='Tracker Id')),
            ],
        ),
    ]
