from django.db import models
from django.db.models import F
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from companies.models import SelfassesmentAccountSubmission, SelfassesmentAccountSubmissionTaxYear


class SelfemploymentIncomeSources(models.Model):
    class Meta:
        verbose_name = "Income Source"
        verbose_name_plural = "Income Sources"
        ordering = [F('index_position').asc(nulls_last=True)]

    name = models.CharField(_("Name"), max_length=255)
    index_position = models.IntegerField('Sorting order', blank=True, null=True)
    backend_identifier = models.CharField('Identifier for application logic', max_length=255, blank=True, null=True)

    def __str__(self)->str:
        return f"IncomeSource(order={self.index_position}, name={self.name})"


class SelfemploymentExpenseSources(models.Model):
    class Meta:
        verbose_name = "Expense Source"
        verbose_name_plural = "Expense Sources"
        ordering = [F('index_position').asc(nulls_last=True)]
    
    name = models.CharField(_("Name"), max_length=255)
    default_personal_usage_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    index_position = models.IntegerField('Sorting order', blank=True, null=True)
    backend_identifier = models.CharField('Identifier for application logic', max_length=255, blank=True, null=True)

    def __str__(self)->str:
        return f"ExpenseSource(order={self.index_position}, name={self.name})"


class SelfemploymentDeductionSources(models.Model):
    class Meta:
        verbose_name = "Deduction Source"
        verbose_name_plural = "Deduction Sources"
        ordering = [F('index_position').asc(nulls_last=True)]
    
    name = models.CharField(_("Name"), max_length=255)
    index_position = models.IntegerField('Sorting order', blank=True, null=True)
    backend_identifier = models.CharField('Identifier for application logic', max_length=255, blank=True, null=True)

    def __str__(self)->str:
        return f"DeductionSource(order={self.index_position}, name={self.name})"


class Months(models.Model):
    class Meta:
        verbose_name = "Month"
        verbose_name_plural = "Months"
        ordering = ['month_index']
    
    month_name = models.CharField(_("Name"), max_length=10)
    month_index = models.IntegerField(_("Index"), default=0)

    def __str__(self)->str:
        return self.month_name


class SelfemploymentIncomesPerTaxYear(models.Model):
    class Meta:
        verbose_name = "Income Per Tax Year"
        verbose_name_plural = "Incomes Per Tax Year"
        ordering = [F('income_source__index_position').asc(nulls_last=True)]
        constraints = [
            models.UniqueConstraint(
                fields=['client', 'month', 'income_source'],
                name="unique_SelfemploymentIncomesPerTaxYear",
                )
        ]

    income_source = models.ForeignKey(SelfemploymentIncomeSources, on_delete=models.CASCADE)
    client = models.ForeignKey(SelfassesmentAccountSubmission, on_delete=models.CASCADE)
    month = models.ForeignKey(Months, on_delete=models.RESTRICT)
    amount = models.FloatField(default=0)
    comission = models.FloatField(default=0)
    note = models.TextField(default='')

    def __str__(self) -> str:
        return f"{self.client.client_id.client_name} - {self.income_source} - {self.month} - {self.amount}"


class SelfemploymentExpensesPerTaxYear(models.Model):
    class Meta:
        verbose_name = "Expense Per Tax Year"
        verbose_name_plural = "Expenses Per Tax Year"
        ordering = [F('expense_source__index_position').asc(nulls_last=True)]
        constraints = [
            models.UniqueConstraint(
                fields=['client', 'month', 'expense_source'], 
                name="unique_SelfemploymentExpensesPerTaxYear",
                )
        ]

    expense_source = models.ForeignKey(SelfemploymentExpenseSources, on_delete=models.CASCADE)
    client = models.ForeignKey(SelfassesmentAccountSubmission, on_delete=models.CASCADE)
    month = models.ForeignKey(Months, on_delete=models.RESTRICT)
    amount = models.FloatField(default=0)
    personal_usage_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    note = models.TextField(default='')

    # this will be used to calculate amount and update data in the backend from the frontend
    # for the expense sources which has backend_identifier value 'office_and_admin_charge'
    # the formula for amount value is `amount = (selfemployment_total_comission*percentage_for_office_and_admin_charge)/100`
    percentage_for_office_and_admin_charge_amount_value = models.FloatField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])

    # this will be used to calculate amount and update data in the backend from the frontend
    # for the expense sources which has backend_identifier value 'fuel'
    # the formula for amount value is `amount = ((income*percentage_for_fuel_amount_value)/100) * (100/(100-personal_usage_percentage))`
    percentage_for_fuel_amount_value = models.FloatField(default=18, validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self) -> str:
        return f"{self.client.client_id.client_name} - {self.expense_source} - {self.month} - {self.amount}"


class SelfemploymentDeductionsPerTaxYear(models.Model):
    class Meta:
        verbose_name = "Deductions Per Tax Year"
        verbose_name_plural = "Deductions Per Tax Year"
        ordering = [F('deduction_source__index_position').asc(nulls_last=True)]
        constraints = [
            models.UniqueConstraint(
                fields=['client', 'deduction_source'],
                name="unique_SelfemploymentDeductionsPerTaxYear",
                )
        ]

    deduction_source = models.ForeignKey(SelfemploymentDeductionSources, on_delete=models.CASCADE)
    client = models.ForeignKey(SelfassesmentAccountSubmission, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    addition = models.FloatField(default=0)
    disposal = models.FloatField(default=0)
    allowance_percentage = models.FloatField(default=18, validators=[MinValueValidator(0), MaxValueValidator(100)])
    personal_usage_percentage = models.FloatField(default=20, validators=[MinValueValidator(0), MaxValueValidator(100)])
    note = models.TextField(default='')

    def __str__(self) -> str:
        return f"{self.client} - {self.deduction_source} - {self.amount}"


class TaxableIncomeSources(models.Model):
    class Meta:
        verbose_name = "Taxable Income Source"
        verbose_name_plural = "Taxable Income Sources"
        ordering = [F('index_position').asc(nulls_last=True)]
    
    name = models.CharField(default="New Taxable Income Source", max_length=255)
    apply_uk_tax = models.BooleanField()
    apply_class2_tax = models.BooleanField()
    apply_class4_tax = models.BooleanField()
    index_position = models.IntegerField('Sorting order', blank=True, null=True)
    backend_identifier = models.CharField('Identifier for application logic', max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return f"TaxableIncomeSource(order={self.index_position}, name={self.name}, uk_tax={self.apply_uk_tax}, class4_tax={self.apply_class4_tax}, class2_tax={self.apply_class2_tax})"

class TaxableIncomeSourceForSubmissionPerTaxYear(models.Model):
    class Meta:
        verbose_name = "Taxable Income Source For Submission"
        verbose_name_plural = "Taxable Income Sources For Submissions"
        ordering = [F('taxable_income_source__index_position').asc(nulls_last=True)]
        constraints = [
            UniqueConstraint(
                fields=['submission', 'taxable_income_source'],
                name="unique_TaxableIncomeSourceForSubmissionPerTaxYear")
            ]
    
    submission = models.ForeignKey(SelfassesmentAccountSubmission, on_delete=models.CASCADE)
    taxable_income_source = models.ForeignKey(TaxableIncomeSources, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    paid_income_tax_amount = models.FloatField(default=0)
    note = models.TextField(default='')

    def __str__(self) -> str:
        return f"{self.submission} - income: {self.amount} - paid tax: {self.paid_income_tax_amount} - income source: {self.taxable_income_source.name}"

class SelfemploymentUkTaxConfigForTaxYear(models.Model):
    class Meta:
        verbose_name = 'Selfemployment UK Tax Config For TaxYear'
        verbose_name_plural = 'Selfemployment UK Tax Configs For TaxYears'
        constraints = [UniqueConstraint(name='unique_tax_year__uk_tax', fields=['tax_year'])]
    
    tax_year = models.ForeignKey(SelfassesmentAccountSubmissionTaxYear, on_delete=models.CASCADE)
    # Allowance reduction configs
    personal_allowance_limit = models.FloatField(default=100000, blank=False, null=True)
    one_pound_reduction_from_PA_earned_over_PAL = models.FloatField(default=2, blank=False, null=True)
    
    # Tax brackets
    personal_allowance = models.FloatField(default=12570, blank=False, null=False)
    basic_rate_max = models.FloatField(default=37700, blank=False, null=False)
    higher_rate_max = models.FloatField(default=150000, blank=False, null=False)
    
    # Applied tax on each brackets
    basic_rate_tax_percentage = models.FloatField(default=20, blank=False, null=True)
    higher_rate_tax_percentage = models.FloatField(default=40, blank=False, null=True)
    additional_rate_tax_percentage = models.FloatField(default=45, blank=False, null=True)

    def __str__(self) -> str:
        return f"{self.tax_year} - {self.personal_allowance}, {self.basic_rate_max}, {self.higher_rate_max}"


class SelfemploymentClass4TaxConfigForTaxYear(models.Model):
    class Meta:
        verbose_name = 'Selfemployment Class 4 Tax Config For TaxYear'
        verbose_name_plural = 'Selfemployment Class 4 Tax Configs For TaxYears'
        constraints = [UniqueConstraint(name='unique_tax_year__class_4_tax', fields=['tax_year'])]
    
    tax_year = models.ForeignKey(SelfassesmentAccountSubmissionTaxYear, on_delete=models.CASCADE)
    basic_rate_min = models.FloatField(default=9500, blank=False)
    basic_rate_max = models.FloatField(default=50000, blank=False)
    basic_rate_tax_percentage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    higher_rate_tax_percentage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self) -> str:
        return f"{self.tax_year} - {self.basic_rate_min} {self.basic_rate_tax_percentage}% - {self.basic_rate_max} {self.higher_rate_tax_percentage}%"


class SelfemploymentClass2TaxConfigForTaxYear(models.Model):
    class Meta:
        verbose_name = 'Selfemployment Class 2 Tax Config For TaxYear'
        verbose_name_plural = 'Selfemployment Class 2 Tax Configs For TaxYears'
        constraints = [UniqueConstraint(name='unique_tax_year__class2_tax', fields=['tax_year'])]
    
    tax_year = models.ForeignKey(SelfassesmentAccountSubmissionTaxYear, on_delete=models.CASCADE)
    tax_applied_for_income_above = models.FloatField(default=6470, blank=False)
    flat_tax_amount = models.FloatField(default=158, blank=False)

    def __str__(self) -> str:
        return f"{self.tax_year} - {self.tax_applied_for_income_above} - {self.flat_tax_amount}"
