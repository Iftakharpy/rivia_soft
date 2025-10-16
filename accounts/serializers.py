from rest_framework import serializers

from companies.serializers import SelfassesmentAccountSubmissionSerializer
from .models import SelfemploymentIncomeSources, SelfemploymentExpenseSources, SelfemploymentDeductionSources, Months, SelfemploymentIncomesPerTaxYear, SelfemploymentExpensesPerTaxYear,  SelfemploymentDeductionsPerTaxYear, TaxableIncomeSources, TaxableIncomeSourceForSubmissionPerTaxYear


class SelfemploymentIncomeSourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelfemploymentIncomeSources
        fields = '__all__'


class SelfemploymentExpenseSourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelfemploymentExpenseSources
        fields = '__all__'


class SelfemploymentDeductionSourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelfemploymentDeductionSources
        fields = '__all__'


class MonthsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Months
        fields = '__all__'


class SelfemploymentIncomesPerTaxYearSerializer(serializers.ModelSerializer):
    # income_source = SelfemploymentIncomeSourcesSerializer()
    # client = SelfassesmentAccountSubmissionSerializer()
    # month = MonthsSerializer()

    class Meta:
        model = SelfemploymentIncomesPerTaxYear
        fields = '__all__'


class SelfemploymentExpensesPerTaxYearSerializer(serializers.ModelSerializer):
    # expense_source = SelfemploymentExpenseSourcesSerializer()
    # client = SelfassesmentAccountSubmissionSerializer()
    # month = MonthsSerializer()

    class Meta:
        model = SelfemploymentExpensesPerTaxYear
        fields = '__all__'


class SelfemploymentDeductionsPerTaxYearSerializer(serializers.ModelSerializer):
    # deduction_source = SelfemploymentDeductionSourcesSerializer()
    # client = SelfassesmentAccountSubmissionSerializer()

    class Meta:
        model = SelfemploymentDeductionsPerTaxYear
        fields = '__all__'


class TaxableIncomeSourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxableIncomeSources
        fields = '__all__'


class TaxableIncomeSourceForSubmissionPerTaxYearSerializer(serializers.ModelSerializer):
    # taxable_income_source = TaxableIncomeSourcesSerializer()

    class Meta:
        model = TaxableIncomeSourceForSubmissionPerTaxYear
        fields = '__all__'
