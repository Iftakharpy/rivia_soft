# Generated by Django 5.1.4 on 2025-01-01 04:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='selfemploymentclass2taxconfigfortaxyear',
            name='tax_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.selfassesmentaccountsubmissiontaxyear'),
        ),
        migrations.AddField(
            model_name='selfemploymentclass4taxconfigfortaxyear',
            name='tax_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.selfassesmentaccountsubmissiontaxyear'),
        ),
        migrations.AddField(
            model_name='selfemploymentdeductionspertaxyear',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.selfassesmentaccountsubmission'),
        ),
        migrations.AddField(
            model_name='selfemploymentdeductionspertaxyear',
            name='deduction_source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.selfemploymentdeductionsources'),
        ),
        migrations.AddField(
            model_name='selfemploymentexpensespertaxyear',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.selfassesmentaccountsubmission'),
        ),
        migrations.AddField(
            model_name='selfemploymentexpensespertaxyear',
            name='expense_source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.selfemploymentexpensesources'),
        ),
        migrations.AddField(
            model_name='selfemploymentexpensespertaxyear',
            name='month',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='accounts.months'),
        ),
        migrations.AddField(
            model_name='selfemploymentincomespertaxyear',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.selfassesmentaccountsubmission'),
        ),
        migrations.AddField(
            model_name='selfemploymentincomespertaxyear',
            name='income_source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.selfemploymentincomesources'),
        ),
        migrations.AddField(
            model_name='selfemploymentincomespertaxyear',
            name='month',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='accounts.months'),
        ),
        migrations.AddField(
            model_name='selfemploymentuktaxconfigfortaxyear',
            name='tax_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.selfassesmentaccountsubmissiontaxyear'),
        ),
        migrations.AddField(
            model_name='taxableincomesourceforsubmission',
            name='submission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.selfassesmentaccountsubmission'),
        ),
        migrations.AddField(
            model_name='taxableincomesourceforsubmission',
            name='taxable_income_source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.taxableincomesources'),
        ),
        migrations.AddConstraint(
            model_name='selfemploymentclass2taxconfigfortaxyear',
            constraint=models.UniqueConstraint(fields=('tax_year',), name='unique_tax_year__class2_tax'),
        ),
        migrations.AddConstraint(
            model_name='selfemploymentclass4taxconfigfortaxyear',
            constraint=models.UniqueConstraint(fields=('tax_year',), name='unique_tax_year__class_4_tax'),
        ),
        migrations.AddConstraint(
            model_name='selfemploymentdeductionspertaxyear',
            constraint=models.UniqueConstraint(fields=('client', 'deduction_source'), name='unique deduction record'),
        ),
        migrations.AddConstraint(
            model_name='selfemploymentexpensespertaxyear',
            constraint=models.UniqueConstraint(fields=('client', 'month', 'expense_source'), name='unique expense record'),
        ),
        migrations.AddConstraint(
            model_name='selfemploymentincomespertaxyear',
            constraint=models.UniqueConstraint(fields=('client', 'month', 'income_source'), name='unique record'),
        ),
        migrations.AddConstraint(
            model_name='selfemploymentuktaxconfigfortaxyear',
            constraint=models.UniqueConstraint(fields=('tax_year',), name='unique_tax_year__uk_tax'),
        ),
    ]
