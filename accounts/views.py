import json

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from django.http import Http404, HttpResponseNotFound
from django.http.request import HttpRequest
from django.template.loader import get_template

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction, connection
from django.db.transaction import TransactionManagementError
from django.db.models import QuerySet
from django.contrib import messages

# Models
from companies.models import SelfassesmentAccountSubmission
from .models import SelfemploymentIncomeSources, SelfemploymentExpenseSources, SelfemploymentDeductionSources, Months, SelfemploymentExpensesPerTaxYear, SelfemploymentIncomesPerTaxYear, SelfemploymentDeductionsPerTaxYear, TaxableIncomeSources, TaxableIncomeSourceForSubmission
from .models import SelfemploymentUkTaxConfigForTaxYear, SelfemploymentClass4TaxConfigForTaxYear, SelfemploymentClass2TaxConfigForTaxYear

# Serializers
from rest_framework.renderers import JSONRenderer
from .serializers import SelfemploymentIncomeSourcesSerializer, SelfemploymentExpenseSourcesSerializer, SelfemploymentDeductionSourcesSerializer, MonthsSerializer, SelfemploymentIncomesPerTaxYearSerializer, SelfemploymentExpensesPerTaxYearSerializer, SelfemploymentDeductionsPerTaxYearSerializer, TaxableIncomeSourcesSerializer, TaxableIncomeSourceForSubmissionSerializer
dump_to_json = JSONRenderer()

from companies.views import URLS, serialized
from companies.decorators import allowed_for_staff, allowed_for_superuser
from companies.url_variables import URL_NAMES, URL_NAMES_PREFIXED_WITH_APP_NAME, URL_PATHS

from .tax_calc_helpers import get_personal_allowance_reduction, percentage_of, uk_tax, uk_class_4_tax


def get_object_or_None(model, *args, pk=None, delete_duplicate=False, return_all=False, select_for_update=False, **kwargs):
    if select_for_update:
        # Check if the function is currently running inside a transaction block (atomic block)
        if not connection.in_atomic_block:
            raise TransactionManagementError(
                "get_object_or_None with select_for_update=True must be called "
                "within an active atomic transaction block (e.g., using @transaction.atomic)."
            )
    try:
        # Start with the base manager
        queryset = model.objects.all()

        if pk is not None:
            # Use .filter() instead of .get() so we can apply select_for_update 
            # and still get a QuerySet to check existence.
            record_qs = queryset.filter(pk=pk, *args, **kwargs)
        else:
            # Filtering by Custom Fields (Composite Key)
            record_qs = queryset.filter(*args, **kwargs)
        
        # Apply select_for_update ONLY to the filtered queryset
        if select_for_update:
            # This ensures the lock is applied only to the specific row(s) identified
            # by the filter, or the index range around them.
            record_qs = record_qs.select_for_update()

        if delete_duplicate and isinstance(record_qs, QuerySet) and len(record_qs) > 1:
            # Note: This operation is now correctly covered by the select_for_update lock.
            for rec in record_qs[1:]:
                rec.delete()
        
        if return_all:
            return record_qs
        
        # Now, try to get the single object
        if record_qs.exists():
            # Retrieve the first object (which is locked if select_for_update=True)
            record = record_qs.first() 
            return record
        else:
            # No object found
            return None
            
    except ObjectDoesNotExist:
        # Should not happen with .filter().exists() but included for safety
        return None
    except MultipleObjectsReturned:
        # This catch is mainly for cases where the PK logic might be wrong elsewhere, but retained.
        return None


@login_required
@allowed_for_staff()
def index(request):
    if request.method=='GET':
        pk = request.GET.get('pk', None)
        account_submission = get_object_or_None(SelfassesmentAccountSubmission, pk=pk)
        
        if not account_submission:
            messages.error(request, f'The SelfassesmentAccountSubmission with pk={pk} does not exist.')
            return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_home_name)
        
        if account_submission.status=='SUBMITTED':
            messages.error(request, 'The submission data you are trying to access is submitted therefore this can not be edited.')
            return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_home_name)
            
        context = {**URLS}
        return render(request, "accounts/index.html", context)
    raise Http404


##############################################################################
## Views to update and insert data for incomes and expenses
##############################################################################
@csrf_exempt
@login_required
def upsert_expese_for_submission(request:HttpRequest, submission_id, month_id, expense_id):
    if not request.method == "POST":
        return HttpResponse(json.dumps({"error": "Invalid request"}), status=400)
    
    try:
        loaded_data = json.loads(request.body.decode())
    except json.decoder.JSONDecodeError:
        return HttpResponse(json.dumps({'error': f'only json data is allowed'}), status=400)

    amount = loaded_data.get("amount", None)
    personal_usage_percentage = loaded_data.get("personal_usage_percentage", None)
    note = loaded_data.get("note", None)

    percentage_for_office_and_admin_charge_amount_value = loaded_data.get("office_and_admin_charge", None)
    percentage_for_fuel_amount_value = loaded_data.get("fuel", None)

    
    if amount is None and personal_usage_percentage is None and note is None and percentage_for_fuel_amount_value is None and percentage_for_office_and_admin_charge_amount_value is None:
        return HttpResponse(json.dumps({'error': f'amount or personal_usage or note or office_and_admin_charge or fuel is required'}), status=400)
    
    if personal_usage_percentage is not None and not 0<=personal_usage_percentage<=100:
        return HttpResponse(json.dumps({'error': f'personal_usage value should be between 0 and 100!'}), status=400)
    
    if percentage_for_office_and_admin_charge_amount_value is not None and not 0<=percentage_for_office_and_admin_charge_amount_value<=100:
        return HttpResponse(json.dumps({'error': f'percentage_for_office_and_admin_charge_amount_value value should be between 0 and 100!'}), status=400)
    
    if percentage_for_fuel_amount_value is not None and not 0<=percentage_for_fuel_amount_value<=100:
        return HttpResponse(json.dumps({'error': f'percentage_for_fuel_amount_value value should be between 0 and 100!'}), status=400)

    # retrive selfassemsent account submission record
    client = get_object_or_None(SelfassesmentAccountSubmission, pk=submission_id, delete_duplicate=True)
    if client is None:
        return HttpResponse(json.dumps({'error': f'SelfassesmentAccountSubmission with pk={submission_id} does not exist'}), status=404)
    
    # retrive month 
    month = get_object_or_None(Months, pk=month_id, delete_duplicate=True)
    if month is None:
        return HttpResponse(json.dumps({'error': f'Month with pk={month_id} does not exist'}), status=404)
    
    # retrive expense source
    expense = get_object_or_None(SelfemploymentExpenseSources, pk=expense_id, delete_duplicate=True)
    if expense is None:
        return HttpResponse(json.dumps({'error': f'Expense with pk={expense_id} does not exist'}), status=404)
    

    is_created = False
    with transaction.atomic():
        expense_for_tax_year, is_created = SelfemploymentExpensesPerTaxYear.objects.get_or_create( 
            client=client,
            month=month,
            expense_source=expense,
            )
        # Update data
        if amount is not None:
            expense_for_tax_year.amount = amount
        if personal_usage_percentage is not None:
            expense_for_tax_year.personal_usage_percentage = personal_usage_percentage
        if note is not None:
            expense_for_tax_year.note = note
        if percentage_for_office_and_admin_charge_amount_value is not None:
            expense_for_tax_year.percentage_for_office_and_admin_charge_amount_value = percentage_for_office_and_admin_charge_amount_value
        if percentage_for_fuel_amount_value is not None:
            expense_for_tax_year.percentage_for_fuel_amount_value = percentage_for_fuel_amount_value
        expense_for_tax_year.save()

    if is_created:
        return HttpResponse(json.dumps({'success': 'Created new record'}), status=201)
    return HttpResponse(json.dumps({'success': 'Updated existing record'}))

@csrf_exempt
@login_required
def upsert_income_for_submission(request:HttpRequest, submission_id, month_id, income_id):
    if not request.method == "POST":
        return HttpResponse(json.dumps({"error": "Invalid request"}), status=400)
    
    try:
        loaded_data = json.loads(request.body.decode())
    except json.decoder.JSONDecodeError:
        return HttpResponse(json.dumps({'error': f'only json data is allowed'}), status=400)
    
    amount = loaded_data.get("amount", None)
    comission = loaded_data.get("comission", None)
    note = loaded_data.get("note", None)

    if amount is None and comission is None and note is None:
        return HttpResponse(json.dumps({'error': f'amount or comission or note must be specified'}), status=400)

    # retrive selfassemsent account submission record
    client = get_object_or_None(SelfassesmentAccountSubmission, pk=submission_id, delete_duplicate=True)
    if client is None:
        return HttpResponse(json.dumps({'error': f'SelfassesmentAccountSubmission with pk={submission_id} does not exist'}), status=404)
    
    # retrive month 
    month = get_object_or_None(Months, pk=month_id, delete_duplicate=True)
    if month is None:
        return HttpResponse(json.dumps({'error': f'Month with pk={month_id} does not exist'}), status=404)
    
    # retrive income source
    income = get_object_or_None(SelfemploymentIncomeSources, pk=income_id, delete_duplicate=True)
    if income is None:
        return HttpResponse(json.dumps({'error': f'IncomeSource with pk={income_id} does not exist'}), status=404)
    
    is_created = False
    with transaction.atomic():
        # Try to retrieve IncomesPerTaxYear if does not exist create it
        income_for_tax_year, is_created = SelfemploymentIncomesPerTaxYear.objects.get_or_create(
            client=client,
            month=month,
            income_source=income,
            )

        # Update the record
        if amount is not None:
            income_for_tax_year.amount = amount
        if comission is not None:
            income_for_tax_year.comission = comission
        if note is not None:
            income_for_tax_year.note = note
        income_for_tax_year.save()
    
    if is_created:
        return HttpResponse(json.dumps({'success': 'Created new record'}), status=201)
    return HttpResponse(json.dumps({'success': 'Updated existing record'}))
    


@csrf_exempt
@login_required
def upsert_deduction_for_submission(request:HttpRequest, submission_id, deduction_id):
    if not request.method == "POST":
        return HttpResponse(json.dumps({"error": "Invalid request"}), status=400)
    
    try:
        loaded_data = json.loads(request.body.decode())
    except json.decoder.JSONDecodeError:
        return HttpResponse(json.dumps({'error': f'only json data is allowed'}), status=400)
    
    amount = loaded_data.get("amount", None)
    addition = loaded_data.get("addition", None)
    disposal = loaded_data.get("disposal", None)
    allowance_percentage = loaded_data.get("allowance_percentage", None)
    personal_usage_percentage = loaded_data.get("personal_usage_percentage", None)
    note = loaded_data.get("note", None)

    if amount is None and addition is None and disposal is None and allowance_percentage is None and personal_usage_percentage is None and note is None:
        return HttpResponse(json.dumps({'error': f'amount or addition or disposal or allowance_percentage or personal_usage_percentage or note must be specified'}), status=400)
    
    if allowance_percentage and not 0<=allowance_percentage<=100:
        return HttpResponse(json.dumps({'error': f'allowance_percentage must be between 0 and 100!'}), status=400)
    if personal_usage_percentage and not 0<=personal_usage_percentage<=100:
        return HttpResponse(json.dumps({'error': f'personal_usage_percentage must be between 0 and 100!'}), status=400)

    # retrive selfassemsent account submission record
    client = get_object_or_None(SelfassesmentAccountSubmission, pk=submission_id, delete_duplicate=True)
    if client is None:
        return HttpResponse(json.dumps({'error': f'SelfassesmentAccountSubmission with pk={submission_id} does not exist'}), status=404)
    
    # retrive deduction source
    deduction_source = get_object_or_None(SelfemploymentDeductionSources, pk=deduction_id, delete_duplicate=True)
    if deduction_source is None:
        return HttpResponse(json.dumps({'error': f'DeductionSource with pk={deduction_id} does not exist'}), status=404)
    

    is_created = False
    with transaction.atomic():
        # Try to retrive IncomesPerTaxYear if does not exist create it
        deduction_for_tax_year, is_created = SelfemploymentDeductionsPerTaxYear.objects.get_or_create(
            client=client,
            deduction_source=deduction_source,
            )

        # Update the record
        if amount is not None:
            deduction_for_tax_year.amount = amount
        if addition is not None:
            deduction_for_tax_year.addition = addition
        if disposal is not None:
            deduction_for_tax_year.disposal = disposal
        if allowance_percentage is not None:
            deduction_for_tax_year.allowance_percentage = allowance_percentage
        if personal_usage_percentage is not None:
            deduction_for_tax_year.personal_usage_percentage = personal_usage_percentage
        if note is not None:
            deduction_for_tax_year.note = note
        deduction_for_tax_year.save()
    
    if is_created:
        return HttpResponse(json.dumps({'success': 'Created new record'}), status=201)
    return HttpResponse(json.dumps({'success': 'Updated existing record'}))
    


@csrf_exempt
@login_required
def upsert_taxable_income_for_submission(request:HttpRequest, submission_id, taxable_income_id):
    if not request.method == "POST":
        return HttpResponse(json.dumps({"error": "Invalid request"}), status=400)
    
    try:
        loaded_data = json.loads(request.body.decode())
    except json.decoder.JSONDecodeError:
        return HttpResponse(json.dumps({'error': f'only json data is allowed'}), status=400)
    
    amount = loaded_data.get("amount", None)
    paid_income_tax_amount = loaded_data.get("paid_income_tax_amount", None)
    note = loaded_data.get("note", None)

    if amount is None and paid_income_tax_amount is None and note is None:
        return HttpResponse(json.dumps({'error': f'amount or paid_income_tax_amount or note must be specified'}), status=400)
    
    # if paid_income_tax_amount and not 0<=paid_income_tax_amount<=100:
    #     return HttpResponse(json.dumps({'error': f'paid_income_tax_amount must be between 0 and 100!'}), status=400)

    # retrive selfassemsent account submission record
    submission = get_object_or_None(SelfassesmentAccountSubmission, pk=submission_id, delete_duplicate=True)
    if submission is None:
        return HttpResponse(json.dumps({'error': f'SelfassesmentAccountSubmission with pk={submission_id} does not exist'}), status=404)
    
    # retrive deduction source
    taxable_income_source = get_object_or_None(TaxableIncomeSources, pk=taxable_income_id, delete_duplicate=True)
    if taxable_income_source is None:
        return HttpResponse(json.dumps({'error': f'DeductionSource with pk={taxable_income_id} does not exist'}), status=404)
    

    is_created = False
    with transaction.atomic():
        # Try to retrive TaxableIncomeSourceForSubmission if does not exist create it
        taxable_income_for_tax_year, is_created = TaxableIncomeSourceForSubmission.objects.get_or_create(
            submission=submission,
            taxable_income_source=taxable_income_source,
            )

        # Update the record
        if amount is not None:
            taxable_income_for_tax_year.amount = amount
        if paid_income_tax_amount is not None:
            taxable_income_for_tax_year.paid_income_tax_amount = paid_income_tax_amount
        if note is not None:
            taxable_income_for_tax_year.note = note
        taxable_income_for_tax_year.save()
    
    if is_created:
        return HttpResponse(json.dumps({'success': 'Created new record'}), status=201)
    return HttpResponse(json.dumps({'success': 'Updated existing record'}))
    


##############################################################################
## Views to return data for incomes and expenses tab
##############################################################################
@login_required
def get_expenses_for_submission(request: HttpRequest, submission_id):
    submission_expenses = SelfemploymentExpensesPerTaxYear.objects.filter(client=submission_id)
    serialized_data = SelfemploymentExpensesPerTaxYearSerializer(submission_expenses, many=True)
    json_response = dump_to_json.render(serialized_data.data)
    return HttpResponse(json_response, content_type='application/json')

@login_required
def get_incomes_for_submission(request: HttpRequest, submission_id):
    submission_incomes = SelfemploymentIncomesPerTaxYear.objects.filter(client=submission_id)
    serialized_data = SelfemploymentIncomesPerTaxYearSerializer(submission_incomes, many=True)
    json_response = dump_to_json.render(serialized_data.data)
    return HttpResponse(json_response, content_type='application/json')

@login_required
def get_deductions_for_submission(request: HttpRequest, submission_id):
    submission_deductions = SelfemploymentDeductionsPerTaxYear.objects.filter(client=submission_id)
    serialized_data = SelfemploymentDeductionsPerTaxYearSerializer(submission_deductions, many=True)
    json_response = dump_to_json.render(serialized_data.data)
    return HttpResponse(json_response, content_type='application/json')

@login_required
def get_taxable_incomes_for_submission(request: HttpRequest, submission_id):
    taxable_incomes = TaxableIncomeSourceForSubmission.objects.filter(submission=submission_id)
    serialized_data = TaxableIncomeSourceForSubmissionSerializer(taxable_incomes, many=True)
    json_response = dump_to_json.render(serialized_data.data)
    return HttpResponse(json_response, content_type='application/json')


##############################################################################
## Views to return data for incomes and expenses tab
##############################################################################
@login_required
def get_all_expense_sources(request):
    expese_sources = SelfemploymentExpenseSources.objects.all()
    serialized = SelfemploymentExpenseSourcesSerializer(expese_sources, many=True)
    json_response = dump_to_json.render(serialized.data)
    return HttpResponse(json_response, content_type='application/json')

@login_required
def get_all_income_sources(request):
    income_sources = SelfemploymentIncomeSources.objects.all()
    serialized = SelfemploymentIncomeSourcesSerializer(income_sources, many=True)
    json_response = dump_to_json.render(serialized.data)
    return HttpResponse(json_response, content_type='application/json')

@login_required
def get_all_months(request):
    income_sources = Months.objects.all()
    serialized = MonthsSerializer(income_sources, many=True)
    json_response = dump_to_json.render(serialized.data)
    return HttpResponse(json_response, content_type='application/json')

@login_required
def get_all_deduction_sources(request):
    deduction_sources = SelfemploymentDeductionSources.objects.all()
    serialized = SelfemploymentDeductionSourcesSerializer(deduction_sources, many=True)
    json_response = dump_to_json.render(serialized.data)
    return HttpResponse(json_response, content_type='application/json')

@login_required
def get_all_taxable_income_sources(request):
    taxable_income_sources = TaxableIncomeSources.objects.all()
    serialized = TaxableIncomeSourcesSerializer(taxable_income_sources, many=True)
    json_response = dump_to_json.render(serialized.data)
    return HttpResponse(json_response, content_type='application/json')



##############################################################################
## Views to calculate and retun tax
##############################################################################


def calculate_selfemployment_expense(expense_amount, personal_usage_percentage):
    personal_usage = (expense_amount*personal_usage_percentage)/100
    expense = expense_amount - personal_usage
    return expense if expense>=0 else 0

def get_total_selfemployment_expense(selfemployment_expenses):
    total = 0
    for expense in selfemployment_expenses:
        total += calculate_selfemployment_expense(expense.amount, expense.personal_usage_percentage)
    return total


def calculate_selfemployment_income(income_amount, comission):
    income = income_amount #- comission
    return income if income>=0 else 0

def get_total_selfemployment_income(selfemployment_incomes):
    total = 0
    for income in selfemployment_incomes:
        total += calculate_selfemployment_income(income.amount, income.comission)
    return total

def get_total_selfemployment_comission(selfemployment_incomes):
    total = 0
    for income in selfemployment_incomes:
        total += income.comission
    return total


def calculate_total_for_deduction_and_allowance(deduction_and_allowance):
    amount = deduction_and_allowance.amount
    addition = deduction_and_allowance.addition
    disposal = deduction_and_allowance.disposal
    return amount + addition + disposal

def calculate_written_down_allowance_for_deduction_and_allowance(deduction_and_allowance):
    allowance_percentage = deduction_and_allowance.allowance_percentage
    total = calculate_total_for_deduction_and_allowance(deduction_and_allowance)
    return (total * allowance_percentage) / 100

def calculate_personal_usage_for_deduction_and_allowance(deduction_and_allowance):
    personal_usage_percentage = deduction_and_allowance.personal_usage_percentage
    allowance = calculate_written_down_allowance_for_deduction_and_allowance(deduction_and_allowance)
    return (allowance * personal_usage_percentage) / 100

def calculate_capital_allowance_for_deduction_and_allowance(deduction_and_allowance):
    personal_usage = calculate_personal_usage_for_deduction_and_allowance(deduction_and_allowance)
    allowance = calculate_written_down_allowance_for_deduction_and_allowance(deduction_and_allowance)
    capital_allowance = allowance - personal_usage
    return capital_allowance if capital_allowance>=0 else 0

def calculate_written_down_value_for_deduction_and_allowance(deduction_and_allowance):
    written_down_allowance = calculate_written_down_allowance_for_deduction_and_allowance(deduction_and_allowance)
    total = calculate_total_for_deduction_and_allowance(deduction_and_allowance)
    return total - written_down_allowance

def get_total_selfemployment_deduction_and_allowance(selfemployment_deductions_and_allowances):
    total = 0
    for deduction in selfemployment_deductions_and_allowances:
        if deduction.deduction_source.backend_identifier=="loss_brought_forward_from_previous_year":
            total += deduction.amount
        else:
            total += calculate_capital_allowance_for_deduction_and_allowance(deduction)
    return total


def calculate_taxable_income(income_amount, paid_tax_amount):
    return income_amount if income_amount>=0 else 0

def get_total_taxable_income(taxable_incomes):
    total = 0
    for income in taxable_incomes:
        total += calculate_taxable_income(income.amount, income.paid_income_tax_amount)
    return total

def get_total_paid_income_tax_from_taxable_incomes(taxable_incomes):
    total = 0
    for taxable_income in taxable_incomes:
        total += taxable_income.paid_income_tax_amount
    return total



class RaiseErrorMessages(Exception):
    def __init__(self, messages=[]) -> None:
        self.messages = messages
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.messages})"

def filter_selfemployment_incomes(selfemployment_incomes):
    return [income for income in selfemployment_incomes if income.amount>0]
def filter_selfemployment_expenses(selfemployment_expenses):
    return [expense for expense in selfemployment_expenses if expense.amount>0]
def filter_taxable_incomes(taxable_incomes):
    return [taxable_income for taxable_income in taxable_incomes if taxable_income.amount>0]
def filter_deductions_and_allowances(deductions_and_allowances):
    return [allowance for allowance in deductions_and_allowances if allowance.amount>0]


def get_total_selfemployment_income_by_submission_id(submission_id):
    """Selfemployment Income (Including Tips)"""
    selfemployment_incomes = get_object_or_None(SelfemploymentIncomesPerTaxYear, delete_duplicate=False, return_all=True, client=submission_id)
    selfemployment_incomes = filter_selfemployment_incomes(selfemployment_incomes)
    return get_total_selfemployment_income(selfemployment_incomes)

def get_total_selfemployment_expense_by_submission_id(submission_id):
    """Selfemployment Expense total of expenses + commission from incomes and deductions from deduction sources"""
    selfemployment_expenses = get_object_or_None(SelfemploymentExpensesPerTaxYear, delete_duplicate=False, return_all=True, client=submission_id)
    selfemployment_expenses = filter_selfemployment_expenses(selfemployment_expenses)

    deductions_and_allowances = get_object_or_None(SelfemploymentDeductionsPerTaxYear, delete_duplicate=False, return_all=True, client=submission_id)
    deductions_and_allowances = filter_deductions_and_allowances(deductions_and_allowances)

    # selfemployment_incomes = get_object_or_None(SelfemploymentIncomesPerTaxYear, delete_duplicate=False, return_all=True, client=submission_id)
    # selfemployment_incomes = filter_selfemployment_incomes(selfemployment_incomes)

    selfemployment_expense = get_total_selfemployment_expense(selfemployment_expenses)
    deduction_and_allowance = get_total_selfemployment_deduction_and_allowance(deductions_and_allowances)
    return selfemployment_expense + deduction_and_allowance

def get_total_selfemployment_net_profit_by_submission_id(submission_id):
    """Selfemployment net profit"""
    total_income = get_total_selfemployment_income_by_submission_id(submission_id)
    total_expense = get_total_selfemployment_expense_by_submission_id(submission_id)
    return total_income-total_expense

def get_total_taxable_income_by_submission_id(submission_id):
    """total taxable income"""
    error_messages = []

    account_submission = get_object_or_None(SelfassesmentAccountSubmission, pk=submission_id, delete_duplicate=True)
    if not account_submission:
        error_messages.append(f"Account submission does not exist for {submission_id} submission id.")
        raise RaiseErrorMessages(error_messages)
    tax_year = account_submission.tax_year
    
    UK_tax_config = get_object_or_None(SelfemploymentUkTaxConfigForTaxYear, delete_duplicate=False, tax_year=tax_year)
    if not UK_tax_config:
        error_messages.append(f"Uk tax configuration for {tax_year} tax-year not found.")
        raise RaiseErrorMessages(error_messages)
    
    taxable_incomes = get_object_or_None(TaxableIncomeSourceForSubmission, delete_duplicate=False, return_all=True, submission=submission_id)
    taxable_incomes = filter_taxable_incomes(taxable_incomes)
    
    total_taxable_income = get_total_taxable_income(taxable_incomes)
    total_income = get_total_selfemployment_net_profit_by_submission_id(submission_id) + total_taxable_income

    personal_allowance_reduction = get_personal_allowance_reduction(
        total_income,
        UK_tax_config.personal_allowance,
        UK_tax_config.personal_allowance_limit,
        UK_tax_config.one_pound_reduction_from_PA_earned_over_PAL)
    reduced_personal_allowance = UK_tax_config.personal_allowance-personal_allowance_reduction

    taxable_income = max(total_income-reduced_personal_allowance, 0)
    return taxable_income

def get_total_tax_by_submission_id(submission_id):
    error_messages = []

    account_submission = get_object_or_None(SelfassesmentAccountSubmission, pk=submission_id, delete_duplicate=True)
    if not account_submission:
        error_messages.append(f"Account submission does not exist for {submission_id} submission id.")
        raise RaiseErrorMessages(error_messages)
    tax_year = account_submission.tax_year

    taxable_incomes = get_object_or_None(TaxableIncomeSourceForSubmission, delete_duplicate=False, return_all=True, submission=submission_id)
    taxable_incomes = filter_taxable_incomes(taxable_incomes)

    UK_tax_config = get_object_or_None(SelfemploymentUkTaxConfigForTaxYear, delete_duplicate=False, tax_year=tax_year)
    Class4_tax_config = get_object_or_None(SelfemploymentClass4TaxConfigForTaxYear, delete_duplicate=False, tax_year=tax_year)
    Class2_tax_config = get_object_or_None(SelfemploymentClass2TaxConfigForTaxYear, delete_duplicate=False, tax_year=tax_year)
    if not UK_tax_config:
        error_messages.append(f'UK tax configuration not found for the year {tax_year.tax_year}!')
    if not Class4_tax_config:
        error_messages.append(f'Class 4 configuration not found for the year {tax_year.tax_year}!')
    if not Class2_tax_config:
        error_messages.append(f'Class 2 configuration not found for the year {tax_year.tax_year}!')
    if error_messages:
        raise RaiseErrorMessages(error_messages)

    # Taxable Incomes
    selfemployment_net_profit = get_total_selfemployment_net_profit_by_submission_id(submission_id)

    uk_tax_applicable_incomes = [income for income in taxable_incomes  if income.taxable_income_source.apply_uk_tax]
    total_income_for_uk_tax = get_total_taxable_income(uk_tax_applicable_incomes)
    total_income_for_uk_tax += selfemployment_net_profit if selfemployment_net_profit>0 else 0

    class_4_tax_applicable_incomes = [income for income in taxable_incomes  if income.taxable_income_source.apply_class4_tax]
    total_income_for_class_4_tax = get_total_taxable_income(class_4_tax_applicable_incomes)
    total_income_for_class_4_tax += selfemployment_net_profit if selfemployment_net_profit>0 else 0

    class_2_tax_applicable_incomes = [income for income in taxable_incomes  if income.taxable_income_source.apply_class2_tax]
    total_income_for_class_2_tax = get_total_taxable_income(class_2_tax_applicable_incomes)
    total_income_for_class_2_tax += selfemployment_net_profit if selfemployment_net_profit>0 else 0


    tax_calc__uk_tax = uk_tax(
        total_income=total_income_for_uk_tax,
        personal_allowance=UK_tax_config.personal_allowance,
        basic_rate_max=UK_tax_config.basic_rate_max,
        higher_rate_max=UK_tax_config.higher_rate_max,
        basic_tax_rate=UK_tax_config.basic_rate_tax_percentage,
        higher_tax_rate=UK_tax_config.higher_rate_tax_percentage,
        additional_tax_rate=UK_tax_config.additional_rate_tax_percentage,
        personal_allowance_limit=UK_tax_config.personal_allowance_limit,
        one_pound_reduction_from_PA_earned_over_PAL=UK_tax_config.one_pound_reduction_from_PA_earned_over_PAL
        )
    tax_calc__class_4_tax = uk_class_4_tax(
        total_income=total_income_for_class_4_tax,
        basic_rate_start=Class4_tax_config.basic_rate_min,
        higher_rate_start=Class4_tax_config.basic_rate_max,
        basic_rate_tax_percentage=Class4_tax_config.basic_rate_tax_percentage,
        higher_rate_tax_percentage=Class4_tax_config.higher_rate_tax_percentage
    )
    tax_calc__class_2_tax = {
            'total': 0 if Class2_tax_config.tax_applied_for_income_above>=total_income_for_class_2_tax else Class2_tax_config.flat_tax_amount
        }
    
    total_tax = tax_calc__uk_tax.total + tax_calc__class_4_tax.total + tax_calc__class_2_tax['total']
    deducton_at_source = get_total_paid_income_tax_from_taxable_incomes(taxable_incomes)
    
    total_tax -= deducton_at_source
    advanced_tax = percentage_of(total_tax, 50) if total_tax>1000 else 0

    due_tax = total_tax + advanced_tax
    # due_tax = max(due_tax, 0)
    return due_tax

@login_required
def overview_section_data(request:HttpRequest, submission_id):
    try:
        selfemployment_income = get_total_selfemployment_income_by_submission_id(submission_id)
        total_taxable_income = get_total_taxable_income_by_submission_id(submission_id)
        total_expense = get_total_selfemployment_expense_by_submission_id(submission_id)
        selfemployment_net_profit = get_total_selfemployment_net_profit_by_submission_id(submission_id)
        total_tax = get_total_tax_by_submission_id(submission_id)
        data = {
            'income': selfemployment_income,
            'expense': total_expense,
            'profit': selfemployment_net_profit,
            'taxable_income': total_taxable_income,
            'tax': total_tax
        }
        return HttpResponse(dump_to_json.render(data))
    except RaiseErrorMessages as e:
        return HttpResponseNotFound(content=dump_to_json.render(e.messages))


# Cache for weasyprint
IMAGE_CACHE = {}
FONT_CONFIG = FontConfiguration()
STYLESHEETS_CACHE = [
        CSS(filename='accounts/templates/accounts/tax_report_style.css'),
    ]
def generate_tax_report_pdf(account_submission):
    template = get_template('accounts/tax_report.html')

    submission_id = account_submission.pk

    tax_year = account_submission.tax_year
    selfemployment_incomes = get_object_or_None(SelfemploymentIncomesPerTaxYear, delete_duplicate=False, return_all=True, client=submission_id)
    selfemployment_incomes = filter_selfemployment_incomes(selfemployment_incomes)
    selfemployment_total_comission = get_total_selfemployment_comission(selfemployment_incomes)

    selfemployment_expenses = get_object_or_None(SelfemploymentExpensesPerTaxYear, delete_duplicate=False, return_all=True, client=submission_id)
    personal_usage_heading_value = selfemployment_expenses.order_by('-personal_usage_percentage')[0].personal_usage_percentage if selfemployment_expenses else 20
    selfemployment_expenses = filter_selfemployment_expenses(selfemployment_expenses)

    taxable_incomes = get_object_or_None(TaxableIncomeSourceForSubmission, delete_duplicate=False, return_all=True, submission=submission_id)
    taxable_incomes = [taxable_income for taxable_income in taxable_incomes if taxable_income.amount>0]
    
    deductions_and_allowances = get_object_or_None(SelfemploymentDeductionsPerTaxYear, delete_duplicate=False, return_all=True, client=submission_id)
    deductions_and_allowances = filter_deductions_and_allowances(deductions_and_allowances)

    # selfemployment
    selfemployment_total_income = get_total_selfemployment_income(selfemployment_incomes)
    selfemployment_total_expense = get_total_selfemployment_expense(selfemployment_expenses)
    selfemployment_total_deduction_and_allowance = get_total_selfemployment_deduction_and_allowance(deductions_and_allowances)

    # Car value calculations
    car_value_deduction_and_allowance = get_object_or_None(SelfemploymentDeductionsPerTaxYear, delete_duplicate=False, return_all=False, client=submission_id, deduction_source__backend_identifier="car_value")
    allowance_car_value = {
        'amount': 0,
        'addition': 0,
        'disposal': 0,
        'personal_usage_percentage': 0,
        'written_down_allowance_percentage': 0,

        'total': 0,
        'written_down_allowance': 0,
        'written_down_value': 0,
        'personal_usage': 0,
        'capital_allowance_deduction': 0,
    }
    if car_value_deduction_and_allowance:
        allowance_car_value['amount'] = car_value_deduction_and_allowance.amount
        allowance_car_value['addition'] = car_value_deduction_and_allowance.addition
        allowance_car_value['disposal'] = car_value_deduction_and_allowance.disposal
        allowance_car_value['personal_usage_percentage'] = car_value_deduction_and_allowance.personal_usage_percentage
        allowance_car_value['written_down_allowance_percentage'] = car_value_deduction_and_allowance.allowance_percentage

        allowance_car_value['total'] = calculate_total_for_deduction_and_allowance(car_value_deduction_and_allowance)
        allowance_car_value['written_down_allowance'] = calculate_written_down_allowance_for_deduction_and_allowance(car_value_deduction_and_allowance)
        allowance_car_value['written_down_value'] = calculate_written_down_value_for_deduction_and_allowance(car_value_deduction_and_allowance)
        allowance_car_value['personal_usage'] = calculate_personal_usage_for_deduction_and_allowance(car_value_deduction_and_allowance)
        allowance_car_value['capital_allowance_deduction'] = calculate_capital_allowance_for_deduction_and_allowance(car_value_deduction_and_allowance)

    # Loss brought forward from previous year
    loss_brought_forward_from_previous_year = get_object_or_None(SelfemploymentDeductionsPerTaxYear, delete_duplicate=False, return_all=False, client=submission_id, deduction_source__backend_identifier="loss_brought_forward_from_previous_year")
    if loss_brought_forward_from_previous_year:
        loss_brought_forward_from_previous_year = loss_brought_forward_from_previous_year.amount if loss_brought_forward_from_previous_year.amount >= 0 else 0
    else:
        loss_brought_forward_from_previous_year = 0

    total_expenses = selfemployment_total_expense + allowance_car_value['capital_allowance_deduction'] + loss_brought_forward_from_previous_year
    selfemployment_net_profit = selfemployment_total_income - total_expenses

    # Income tax page calculations
    # Tax configs
    error_messages = []
    UK_tax_config = get_object_or_None(SelfemploymentUkTaxConfigForTaxYear, delete_duplicate=False, tax_year=tax_year)
    Class4_tax_config = get_object_or_None(SelfemploymentClass4TaxConfigForTaxYear, delete_duplicate=False, tax_year=tax_year)
    Class2_tax_config = get_object_or_None(SelfemploymentClass2TaxConfigForTaxYear, delete_duplicate=False, tax_year=tax_year)
    if not UK_tax_config:
        error_messages.append(f'UK tax configuration not found for the year {tax_year.tax_year}!')
    if not Class4_tax_config:
        error_messages.append(f'Class 4 configuration not found for the year {tax_year.tax_year}!')
    if not Class2_tax_config:
        error_messages.append(f'Class 2 configuration not found for the year {tax_year.tax_year}!')

    total_income_from_taxable_incomes = get_total_taxable_income(taxable_incomes)
    total_income = total_income_from_taxable_incomes
    total_income += selfemployment_net_profit if selfemployment_net_profit>0 else 0

    tax_calc_data={}
    if not error_messages:
        # Personal Allowance
        personal_allowance = UK_tax_config.personal_allowance
        personal_allowance_limit = UK_tax_config.personal_allowance_limit
        one_unit_deducted_from_PA_earned_over_PAL = UK_tax_config.one_pound_reduction_from_PA_earned_over_PAL
        
        personal_allowance_reduction = get_personal_allowance_reduction(total_income, personal_allowance, personal_allowance_limit, one_unit_deducted_from_PA_earned_over_PAL)
        reduced_personal_allowance = personal_allowance-personal_allowance_reduction

        # Taxable Incomes
        uk_tax_applicable_incomes = [income for income in taxable_incomes  if income.taxable_income_source.apply_uk_tax]
        total_income_for_uk_tax = get_total_taxable_income(uk_tax_applicable_incomes)
        total_income_for_uk_tax += selfemployment_net_profit if selfemployment_net_profit>0 else 0

        class_4_tax_applicable_incomes = [income for income in taxable_incomes  if income.taxable_income_source.apply_class4_tax]
        total_income_for_class_4_tax = get_total_taxable_income(class_4_tax_applicable_incomes)
        total_income_for_class_4_tax += selfemployment_net_profit if selfemployment_net_profit>0 else 0

        class_2_tax_applicable_incomes = [income for income in taxable_incomes  if income.taxable_income_source.apply_class2_tax]
        total_income_for_class_2_tax = get_total_taxable_income(class_2_tax_applicable_incomes)
        total_income_for_class_2_tax += selfemployment_net_profit if selfemployment_net_profit>0 else 0


        # Tax Calculation page data
        taxable_income = total_income - reduced_personal_allowance
        taxable_income = max(taxable_income, 0)
        tax_calc__income = {
            'total_income': total_income,
            'personal_allowance': personal_allowance,
            'reduced_personal_allowance': reduced_personal_allowance,
            'taxable_income': taxable_income
        }
        
        tax_calc__uk_tax = uk_tax(
            total_income=total_income_for_uk_tax,
            personal_allowance=personal_allowance,
            basic_rate_max=UK_tax_config.basic_rate_max,
            higher_rate_max=UK_tax_config.higher_rate_max,
            basic_tax_rate=UK_tax_config.basic_rate_tax_percentage,
            higher_tax_rate=UK_tax_config.higher_rate_tax_percentage,
            additional_tax_rate=UK_tax_config.additional_rate_tax_percentage,
            personal_allowance_limit=UK_tax_config.personal_allowance_limit,
            one_pound_reduction_from_PA_earned_over_PAL=UK_tax_config.one_pound_reduction_from_PA_earned_over_PAL
            )
        tax_calc__class_4_tax = uk_class_4_tax(
            total_income=total_income_for_class_4_tax,
            basic_rate_start=Class4_tax_config.basic_rate_min,
            higher_rate_start=Class4_tax_config.basic_rate_max,
            basic_rate_tax_percentage=Class4_tax_config.basic_rate_tax_percentage,
            higher_rate_tax_percentage=Class4_tax_config.higher_rate_tax_percentage
        )
        tax_calc__class_2_tax = {
                    'earning_limit': Class2_tax_config.tax_applied_for_income_above,
                    'total': 0 if Class2_tax_config.tax_applied_for_income_above>=total_income_for_class_2_tax else Class2_tax_config.flat_tax_amount
                }
        
        tax_calc__total_tax = tax_calc__uk_tax.total + tax_calc__class_4_tax.total + tax_calc__class_2_tax['total']
        tax_calc__total_paid_tax = get_total_paid_income_tax_from_taxable_incomes(taxable_incomes)
        tax_calc__total_tax_due = tax_calc__total_tax - tax_calc__total_paid_tax
        tax_calc__adv_tax = percentage_of(tax_calc__total_tax_due, 50) if tax_calc__total_tax_due>1000 else 0
        net_total_tax = tax_calc__adv_tax + tax_calc__total_tax_due

        tax_calc_data = {
            'income': tax_calc__income,
            'uk_tax': tax_calc__uk_tax,
            'class_4': tax_calc__class_4_tax,
            'class_2': tax_calc__class_2_tax,
            'total_tax': tax_calc__total_tax,
            'total_paid_tax': tax_calc__total_paid_tax,
            'total_tax_due': tax_calc__total_tax_due,
            'adv_tax': tax_calc__adv_tax,
            'net_total_tax': net_total_tax
        }
    
    context = {
        # submission info
        'submission': account_submission,
        'tax_year': tax_year.tax_year,
        'tax_year_next': tax_year.tax_year[5:],
        'tax_year_prev': tax_year.tax_year[:4],
        'tax_year_prev_prev': int(tax_year.tax_year[:4])-1,

        # client info
        'client_name': account_submission.client_id.client_name,
        'client_address': account_submission.client_id.personal_address,
        'client_post_code': account_submission.client_id.personal_post_code,

        # selfemployment
        'selfemployment_total_income': get_total_selfemployment_income(selfemployment_incomes),
        'selfemployment_total_income_comission': selfemployment_total_comission,
        'selfemployment_total_expense': selfemployment_total_expense,
        'selfemployment_total_expense_with_car_value': selfemployment_total_expense + allowance_car_value['capital_allowance_deduction'],
        'selfemployment_total_deduction_and_allowance': get_total_selfemployment_deduction_and_allowance(deductions_and_allowances),
        'profit_for_the_year': selfemployment_total_income - allowance_car_value['capital_allowance_deduction'] - selfemployment_total_expense,
        'selfemployment_net_profit': selfemployment_net_profit,
        'selfemployment_is_loss': selfemployment_net_profit<0,
        'total_expenses': total_expenses,

        'total_taxable_income': get_total_taxable_income(taxable_incomes),

        # client's income and expenses info
        'selfemployment_incomes': selfemployment_incomes,
        'selfemployment_expenses': selfemployment_expenses,
        'personal_usage_heading_value': personal_usage_heading_value,
        'deductions_and_allowances': deductions_and_allowances,
        'taxable_incomes': taxable_incomes,
        'car_value': allowance_car_value,
        'loss_brought_forward_from_previous_year': loss_brought_forward_from_previous_year,

        # Income Tax calculation page
        'tax_calc': {
            'errors': error_messages,
            **tax_calc_data
        },
    }
    
    # Initiate file like HttpResponse object
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f"inline; filename=Account of {context['submission'].client_id.client_name} Tax Year-{tax_year.tax_year}.pdf"
    
    # Render html template to string
    html_markup = template.render(context)

    # Generate and write pdf to HttpResponse
    weasyprinted_markup = HTML(string=html_markup)
    weasyprinted_markup.write_pdf(response, stylesheets=STYLESHEETS_CACHE, font_config=FONT_CONFIG, image_cache=IMAGE_CACHE)

    return response

@login_required
def tax_report_pdf(request:HttpRequest, submission_id):
    account_submission = get_object_or_None(SelfassesmentAccountSubmission, pk=submission_id, delete_duplicate=True)

    if not account_submission:
        raise Http404("Submission for the submission_id specified does not exist!")

    return generate_tax_report_pdf(account_submission)


def public_tax_report_pdf(request:HttpRequest, submission_id, view_key):
    account_submission = get_object_or_None(SelfassesmentAccountSubmission, pk=submission_id, delete_duplicate=True)

    if not account_submission or account_submission.unique_public_view_key!=view_key:
        raise Http404("Invalid view key!")

    return generate_tax_report_pdf(account_submission)
