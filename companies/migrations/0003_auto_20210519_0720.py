# Generated by Django 3.2.2 on 2021-05-19 01:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='selfassesment',
            name='date_of_registration',
            field=models.DateField(default=django.utils.timezone.localtime, verbose_name='Registration date'),
        ),
        migrations.AlterField(
            model_name='selfassesmentaccountsubmission',
            name='date_of_submission',
            field=models.DateField(blank=True, default=django.utils.timezone.localtime, null=True, verbose_name='Submission date'),
        ),
        migrations.AlterField(
            model_name='selfassesmenttracker',
            name='creation_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.localtime, editable=False, verbose_name='Tracker creation datetime'),
        ),
        migrations.AlterField(
            model_name='selfassesmenttracker',
            name='deadline',
            field=models.DateField(default=django.utils.timezone.localtime, verbose_name='Deadline'),
        ),
    ]