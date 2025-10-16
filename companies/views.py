from datetime import timedelta
from dateutil.relativedelta import relativedelta
import calendar
from datetime import date

import json
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.core.serializers import serialize
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse, Http404
from django.db.utils import IntegrityError
from django.db.models import DurationField, F, ExpressionWrapper, Q, QuerySet
from django.urls.exceptions import NoReverseMatch
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required


#forms
from .forms import SelfassesmentCreationForm, SelfassesmentChangeForm, SelfassesmentDeleteForm
from .forms import SelfemploymentIncomeAndExpensesDataCollectionCreationForm, SelfemploymentIncomeAndExpensesDataCollectionUpdateForm, \
  SelfemploymentIncomeAndExpensesDataCollectionDeleteForm, SelfemploymentIncomeAndExpensesDataCollectionCreationFormForClients, \
  SelfemploymentIncomeAndExpensesDataCollectionAuthFormForClients
from .forms import SelfassesmentAccountSubmissionCreationForm, SelfassesmentAccountSubmissionChangeForm, SelfassesmentAccountSubmissionDeleteForm
from .forms import Add_All_Selfassesment_to_SelfassesmentAccountSubmission_Form
from .forms import SelfassesmentTrackerCreationForm, SelfassesmentTrackerChangeForm, SelfassesmentTrackerDeleteForm

from .forms import LimitedCreationForm, LimitedChangeForm, LimitedDeleteForm
from .forms import LimitedOnboardingForm
from .forms import LimitedTrackerCreationForm, LimitedTrackerChangeForm, LimitedTrackerDeleteForm
from .forms import MergedTrackerCreateionForm
from .forms import LimitedSubmissionDeadlineTrackerCreationForm, LimitedSubmissionDeadlineTrackerChangeForm, LimitedSubmissionDeadlineTrackerDeleteForm
from .forms import LimitedVATTrackerCreationForm, LimitedVATTrackerChangeForm, LimitedVATTrackerDeleteForm
from .forms import LimitedConfirmationStatementTrackerCreationForm, LimitedConfirmationStatementTrackerChangeForm, LimitedConfirmationStatementTrackerDeleteForm

#models
from django.db.models import Subquery
from .models import Selfassesment, SelfassesmentTracker, SelfassesmentAccountSubmission, SelfassesmentAccountSubmissionTaxYear, SelfemploymentIncomeAndExpensesDataCollection
from .models import Limited, LimitedTracker, LimitedSubmissionDeadlineTracker, LimitedVATTracker, LimitedConfirmationStatementTracker
from .models import AutoCreatedSelfassesmentTracker
from .models import OnboardingTask, LimitedOnboardingTasks

# Serializers
from rest_framework.renderers import JSONRenderer
from .serializers import SelfassesmentAccountSubmissionSerializer
dump_model_to_json = JSONRenderer()

#export
from .export_models import export_to_csv

#queries
from .queries import db_search_Selfassesment, db_all_Selfassesment
from .queries import db_search_SelfemploymentIncomeAndExpensesDataCollection, db_all_SelfemploymentIncomeAndExpensesDataCollection
from .queries import db_search_SelfassesmentAccountSubmissionTaxYear, db_all_SelfassesmentAccountSubmissionTaxYear
from .queries import db_search_SelfassesmentAccountSubmission, db_all_SelfassesmentAccountSubmission
from .queries import db_search_SelfassesmentTracker, db_all_SelfassesmentTracker

from .queries import db_all_Limited, db_search_Limited
from .queries import db_search_LimitedTracker, db_all_LimitedTracker
from .queries import db_search_LimitedSubmissionDeadlineTracker, db_all_LimitedSubmissionDeadlineTracker
from .queries import db_search_LimitedVATTracker, db_all_LimitedVATTracker
from .queries import db_search_LimitedConfirmationStatementTracker, db_all_LimitedConfirmationStatementTracker

# serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CustomUserSerializer, SelfassesmentAccountSubmissionTaxYearSerializer, SelfassesmentSerializer, LimitedSerializer

#permissions
from .decorators import allowed_for_staff, allowed_for_superuser


from .utils import model_field_to_form_meta


from .url_variables import APPLICATION_NAME, URL_NAMES, URL_PATHS, Full_URL_PATHS_WITHOUT_ARGUMENTS, URL_NAMES_PREFIXED_WITH_APP_NAME
from .url_variables import *

# html generator
from .utils import get_field_names_with_label, group_fields_by_uniqueness
from .html_generator import get_field_names_from_model, generate_template_tag_for_model, generate_data_container_table
from .repr_formats import HTML_Generator, Forms as FK_Formats




application_name = APPLICATION_NAME
# these path names will be passed to templates to use in the navbar links
URLS = {
  'home': f'{application_name}:home',

  **Full_URL_PATHS_WITHOUT_ARGUMENTS.get_dict(),
  **URL_NAMES_PREFIXED_WITH_APP_NAME.get_dict()
}
user_details_url_without_argument = '/u/details/'


def get_object_or_None(model, *args, pk=None, delete_duplicate=False, return_all=False,**kwargs):
    try:
        if pk is not None:
            record = model.objects.get(pk=pk)
        else:
            record = model.objects.filter(*args, **kwargs).order_by('pk')
            if delete_duplicate:
                if type(record) is QuerySet and len(record)>1:
                    for rec in record[1:]:
                        rec.delete()
            if return_all:
                return record
            if record:
                record = record[0]
            if type(record) is QuerySet and len(record) == 0:
                return None
        return record
    except ObjectDoesNotExist:
        return None



SELFASSESMENT_FK_FIELDS_FOR_EXPORT = [ # 'all'
  'client_name',
  'client_file_number',
  'personal_phone_number',
  'personal_post_code',
]
LIMITED_FK_FIELDS_FOR_EXPORT = [ # 'all'
  'client_name',
  'client_file_number',
  'company_reg_number',
  # 'director_phone_number',
  # 'director_post_code'
]
# =============================================================================================================
# =============================================================================================================
# Selfassesment
def get_selfassesment_where_UTR_NOT_SET():
  return Selfassesment.objects.filter(UTR=None)

def get_selfassesment_where_AGENT_NOT_ACTIVE():
  return Selfassesment.objects.filter(HMRC_agent=False)

def get_selfassesment_where_Client_IS_ACTIVE():
  return Selfassesment.objects.filter(is_active=True)

def get_selfassesment_where_Client_IS_INACTIVE():
  return Selfassesment.objects.filter(is_active=False)

def get_selfassesment_which_are_not_added_in_selfassesment_account_submission(tax_year=None):
  if tax_year==None:
    tax_year = SelfassesmentAccountSubmissionTaxYear.get_max_year()
  selfassesment_account_submission_created_for_selfassesments = SelfassesmentAccountSubmission.objects.filter(tax_year=tax_year)
  return Selfassesment.objects.exclude(pk__in=Subquery(selfassesment_account_submission_created_for_selfassesments.values('client_id')))

def get_selfassesment_where_driving_license_expiry_date_is_less_than_3_months():
  return Selfassesment.objects.filter(driving_license_expiry_date__gte=timezone.now()).filter(driving_license_expiry_date__lte=timezone.now()+relativedelta(months=3))
def get_selfassesment_where_passport_expiry_date_is_less_than_3_months():
  return Selfassesment.objects.filter(passport_expiry_date__gte=timezone.now()).filter(passport_expiry_date__lte=timezone.now()+relativedelta(months=3))

def get_selfassesment_where_driving_license_expired():
  return Selfassesment.objects.filter(driving_license_expiry_date__lte=timezone.now())
def get_selfassesment_where_passport_expired():
  return Selfassesment.objects.filter(passport_expiry_date__lte=timezone.now())


@login_required
def home_selfassesment(request):
  current_tax_year = SelfassesmentAccountSubmissionTaxYear.get_max_year()
  pk_field = 'client_id'
  exclude_fields = []
  include_fields = ['client_rating', 'client_name', 'client_file_number', 'is_active', 'start_date', 'HMRC_agent', 'incomplete_tasks', 'personal_phone_number', 'personal_email', 'UTR', 'NINO', "created_by", "date_of_registration", 'driving_license_expiry_date', 'passport_expiry_date', ]
  keep_include_fields = True
  show_others = False
  model_fields = get_field_names_from_model(Selfassesment)
  model_fields.append('incomplete_tasks')
  context = {
    **URLS,
    'caption': 'View Selfassesment',
    'page_title': 'View Selfassesment',
    
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_create_name,
    'export_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_export_name,

    'template_tag': generate_template_tag_for_model(Selfassesment, pk_field=pk_field, show_id=False, exclude_fields=exclude_fields, include_fields=include_fields, keep_include_fields=keep_include_fields, show_others=show_others),
    'data_container': generate_data_container_table(Selfassesment, pk_field=pk_field, show_id=False, exclude_fields=exclude_fields, include_fields=include_fields, keep_include_fields=keep_include_fields, show_others=show_others),

    "counts": True,
    "selfassesment_counts": True,
    "selfassesment_UTR_NOT_SET": get_selfassesment_where_UTR_NOT_SET().count(),
    "selfassesment_AGENT_NOT_ACTIVE": get_selfassesment_where_AGENT_NOT_ACTIVE().count(),
    "selfassesment_Client_IS_ACTIVE": get_selfassesment_where_Client_IS_ACTIVE().count(),
    "selfassesment_Client_IS_INACTIVE": get_selfassesment_where_Client_IS_INACTIVE().count(),
    "selfassesment_not_added_in_selfassesment_account_submission": get_selfassesment_which_are_not_added_in_selfassesment_account_submission(tax_year=current_tax_year).count(),
    "selfassesment_where_driving_license_expiry_date_is_less_than_3_months": get_selfassesment_where_driving_license_expiry_date_is_less_than_3_months().count(),
    "selfassesment_where_passport_expiry_date_is_less_than_3_months": get_selfassesment_where_passport_expiry_date_is_less_than_3_months().count(),
    "selfassesment_where_driving_license_expired": get_selfassesment_where_driving_license_expired().count(),
    "selfassesment_where_passport_expired": get_selfassesment_where_passport_expired().count(),

    'frontend_data':{
      'all_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_viewall_url,
      'search_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_search_url,
      'update_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_update_url,
      'delete_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_delete_url,  
      'model_fields': model_fields
    },
    "export_field_names": group_fields_by_uniqueness({
      "Selfassesment": get_field_names_with_label(Selfassesment),
    })
  }
  return render(request=request, template_name='companies/home.html', context=context)

@login_required
def view_selfassesment(request):
  return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_home_name)

@login_required
def create_selfassesment(request):
  context = {
    **URLS,
    'page_title': 'Create Selfassesment',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_home_name,
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_create_name,
    'form_title': 'Selfassesment Account Year Assign Form',
    'form': SelfassesmentCreationForm(initial={'client_file_number': Selfassesment.get_next_file_number()})
  }

  if request.method == 'POST':
    form = SelfassesmentCreationForm(request.POST)
    context['form'] = form
    if form.is_valid():
      assesment = form.save()
      assesment.set_defaults()
      assesment.created_by = request.user
      assesment.save()
      
      job_description = 'Issues\n'

      if not assesment.UTR:
        # Create Tracker
        tracker = SelfassesmentTracker()
        tracker.client_id = assesment
        tracker.deadline = timezone.now() + relativedelta(days=2)
        tracker.has_issue = True
        tracker.new_customer = True
        tracker.job_description = job_description + '    - Apply/ask for UTR\n'
        tracker.save()
        messages.success(request, f"New Selfassesment Tracker has been created for {assesment} because it doesn't have UTR!")

        # Save reference
        reference = AutoCreatedSelfassesmentTracker(
          selfassesment = assesment,
          selfassesment_tracker = tracker,
          reference = AutoCreatedSelfassesmentTracker.CreatedForField.UTR)
        reference.save()

      if not assesment.NINO:
        # Create Tracker
        tracker = SelfassesmentTracker()
        tracker.client_id = assesment
        tracker.deadline = timezone.now() + relativedelta(days=2)
        tracker.has_issue = True
        tracker.new_customer = True
        tracker.job_description = job_description + '    - Ask for NINO\n'
        tracker.save()
        messages.success(request, f"New Selfassesment Tracker has been created for {assesment} because it doesn't have NINO!")

        # Save reference
        reference = AutoCreatedSelfassesmentTracker(
          selfassesment = assesment,
          selfassesment_tracker = tracker,
          reference = AutoCreatedSelfassesmentTracker.CreatedForField.NINO)
        reference.save()

      if not assesment.HMRC_agent:
        # Create Tracker
        tracker = SelfassesmentTracker()
        tracker.client_id = assesment
        tracker.deadline = timezone.now() + relativedelta(days=2)
        tracker.has_issue = True
        tracker.new_customer = True
        tracker.job_description = job_description + '    - Apply for agent\n'
        tracker.save()
        messages.success(request, f"New Selfassesment Tracker has been created for {assesment} because HMRC agent is inactive!")
        
        # Save reference
        reference = AutoCreatedSelfassesmentTracker(
          selfassesment = assesment,
          selfassesment_tracker = tracker,
          reference = AutoCreatedSelfassesmentTracker.CreatedForField.HMRC_AGENT)
        reference.save()

      context['form'] = SelfassesmentCreationForm(initial={'client_file_number': Selfassesment.get_next_file_number()})
  return render(request, template_name='companies/create.html', context=context)

@login_required
def get_details_selfassesment(request, client_id=None):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    record = get_object_or_404(Selfassesment, client_id=client_id)
    response = SelfassesmentSerializer(instance=record).data
    return HttpResponse(json.dumps(response))
  raise Http404

def mark_tracker_complete(tracker:SelfassesmentTracker)->None:
  tracker.is_completed = True
  tracker.has_issue = False
  tracker.save()

@login_required
def update_selfassesment(request, client_id:int):
  hide_navbar = False
  if request.method=='GET':
    hide_navbar = request.GET.get('hide_navbar', False)
  context = {
    **URLS,
    'page_title': f'Update Selfassesment',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_home_name,
    'id': client_id,
    'update_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_update_name,
    'form_title': 'Selfassesment Update Form',
    'form': SelfassesmentChangeForm(),
    'hide_navbar': hide_navbar
  }

  try:
    record =  Selfassesment.objects.get(client_id=client_id)
    current_is_active_value = record.is_active
    context['form'] = SelfassesmentChangeForm(instance=record)
  except Selfassesment.DoesNotExist:
    messages.error(request, f'Selfassesment Account having id {client_id} does not exists!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_home_name)
    raise Http404

  if request.method == 'POST':
    form = SelfassesmentChangeForm(request.POST, instance=record)
    context['form'] = form
    if form.is_valid():
      # Prevent non admin users from updating active status
      if form.cleaned_data.get('is_active')!=current_is_active_value and not request.user.is_superuser:
        form.add_error('is_active', 'Only admins can change the active status.')
        messages.error(request, 'Update failed due to permission error.')
        return render(request, template_name='companies/update.html', context=context)

      assesment = form.save()
      # Update auto created trackers as compeleted
      if assesment.UTR:
        reference = AutoCreatedSelfassesmentTracker.objects.filter(
          selfassesment = assesment,
          reference = AutoCreatedSelfassesmentTracker.CreatedForField.UTR
          ).first()
        if reference:
          tracker = reference.selfassesment_tracker
          mark_tracker_complete(tracker)
          reference.delete()

      if assesment.NINO:
        reference = AutoCreatedSelfassesmentTracker.objects.filter(
          selfassesment = assesment,
          reference = AutoCreatedSelfassesmentTracker.CreatedForField.NINO
          ).first()
        if reference:
          tracker = reference.selfassesment_tracker
          mark_tracker_complete(tracker)
          reference.delete()

      if assesment.HMRC_agent:
        reference = AutoCreatedSelfassesmentTracker.objects.filter(
          selfassesment = assesment,
          reference = AutoCreatedSelfassesmentTracker.CreatedForField.HMRC_AGENT
          ).first()
        if reference:
          tracker = reference.selfassesment_tracker
          mark_tracker_complete(tracker)
          reference.delete()
      
      messages.success(request, f'Selfassesment has been updated having id {client_id}!')
    else:
      messages.error(request, f'Updating Selfassesment {client_id} failed due to invalid data!')
  return render(request, template_name='companies/update.html', context=context)

@login_required
@allowed_for_superuser(
  message="Sorry! You are not authorized to delete this.",
  redirect_to=URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_home_name)
def delete_selfassesment(request, client_id:int):
  context = {
    **URLS,
    'page_title': 'Delete Selfassesment',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_home_name,
    'id': client_id,
    'delete_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_delete_name,
    'form_title': "Selfassesment Delete Form",
    'form': SelfassesmentDeleteForm()
  }
  try:
    record =  Selfassesment.objects.get(client_id=client_id)
  except Selfassesment.DoesNotExist:
    messages.error(request, f'Selfassesment record with id {client_id}, you are looking for does not exist!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_home_name)

  if request.method == 'POST':
    form = SelfassesmentDeleteForm(request.POST)
    context['form'] = form
    if form.is_valid():
      record.delete()
      messages.success(request, f'Selfassesment has been deleted having id {client_id}!')
    else:
      messages.error(request, f'Selfassesment deletion of id {client_id} failed!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_home_name)
  return render(request, template_name='companies/delete.html', context=context)

@login_required
def search_selfassesment(request, limit: int=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    search_text = request.GET.get('q', '')

    # if tasks query paramter exists then return tasks
    if request.GET.get('tasks'):
      current_tax_year = SelfassesmentAccountSubmissionTaxYear.get_max_year()
      tasks = {
        "selfassesment_UTR_NOT_SET": get_selfassesment_where_UTR_NOT_SET(),
        "selfassesment_AGENT_NOT_ACTIVE": get_selfassesment_where_AGENT_NOT_ACTIVE(),
        "selfassesment_Client_IS_ACTIVE": get_selfassesment_where_Client_IS_ACTIVE(),
        "selfassesment_Client_IS_INACTIVE": get_selfassesment_where_Client_IS_INACTIVE(),
        "selfassesment_not_added_in_selfassesment_account_submission": get_selfassesment_which_are_not_added_in_selfassesment_account_submission(tax_year=current_tax_year),
        "selfassesment_where_driving_license_expiry_date_is_less_than_3_months": get_selfassesment_where_driving_license_expiry_date_is_less_than_3_months(),
        "selfassesment_where_passport_expiry_date_is_less_than_3_months": get_selfassesment_where_passport_expiry_date_is_less_than_3_months(),
        "selfassesment_where_driving_license_expired": get_selfassesment_where_driving_license_expired(),
        "selfassesment_where_passport_expired": get_selfassesment_where_passport_expired(),
      }
      records = tasks.get(request.GET.get('tasks'), [])
      data = serialize(queryset=records, format='json')
      return HttpResponse(data, content_type='application/json')

    if search_text.strip()=='':
      return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Tracker_viewall_name)
    records = db_search_Selfassesment(search_text, limit)
    records = records.order_by("-client_file_number")
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
def all_selfassesment(request, limit=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    records = db_all_Selfassesment(limit)
    records = records.order_by("-client_file_number")
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
@allowed_for_superuser(
  message="Sorry! You are not authorized to export this.",
  redirect_to=URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_home_name)
def export_selfassesment(request):
  response = HttpResponse(
    content_type='text/csv',
    headers={'Content-Disposition': f'attachment; filename="selfassesment_{timezone.localtime()}.csv"'},
  )
  # get field names to export these are in '.' separated format for nested fields
  params = request.GET
  field_names = params.get('export_fields', None)
  if field_names:
    field_names = field_names.split(",")
  else:
    field_names = []
  
  default_include_fields = ['is_active', 'client_file_number', 'client_name', 'personal_phone_number', 'personal_email', 'UTR', 'NINO', 'HMRC_agent']
  include_fields = field_names if len(field_names)>0 else default_include_fields
  exclude_fields = []
  keep_include_fields = True
  show_others = (include_fields==default_include_fields)
  export_to_csv(
    django_model = Selfassesment,
    write_to = response,
    include_fields = include_fields,
    exclude_fields = exclude_fields,
    keep_include_fields = keep_include_fields,
    show_others = show_others
    )
  return response

@api_view(['GET'])
def serialized(request):
  
  return SelfassesmentSerializer()



# =============================================================================================================
# =============================================================================================================
# SelfassesmentAccountSubmissionTaxYear

@login_required
def get_details_selfassesment_account_submission_tax_year(request, id=None):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    record = get_object_or_404(SelfassesmentAccountSubmissionTaxYear, id=id)
    response = SelfassesmentAccountSubmissionTaxYearSerializer(instance=record).data
    return HttpResponse(json.dumps(response))
  raise Http404

@login_required
def search_selfassesment_account_submission_tax_year(request, limit: int=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    search_text = request.GET.get('q', '')
    if search_text.strip()=='':
      return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_viewall_name)
    records = db_search_SelfassesmentAccountSubmissionTaxYear(search_text, limit)
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
def all_selfassesment_account_submission_tax_year(request, limit=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    records = db_all_SelfassesmentAccountSubmissionTaxYear(limit)
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404


# =============================================================================================================
# =============================================================================================================
# SelfemploymentIncomeAndExpensesDataCollection
def slefassesment_account_submission_auto_row(request, selfassesment, tax_year, message=False):
  try:
    account_sumbission = SelfassesmentAccountSubmission(client_id=selfassesment, tax_year=tax_year)
    account_sumbission.save()
  except Exception:
    if message:
      messages.error(request, "Failed auto creation of Selfassesment Account Submission a row already exists.")

def get_selfassesment_data_collection_row_count():
  return SelfemploymentIncomeAndExpensesDataCollection.objects.filter()

@login_required
def home_selfassesment_data_collection(request):
  current_tax_year = SelfassesmentAccountSubmissionTaxYear.get_max_year()
  pk_field = 'id'
  exclude_fields = []
  include_fields = ['selfassesment', 'tax_year', 'is_submitted']
  keep_include_fields = True
  show_others = True
  model_fields = get_field_names_from_model(SelfemploymentIncomeAndExpensesDataCollection)
  context = {
    **URLS,
    'page_title': 'View Selfassesment Data Collection',
    'caption': mark_safe('View <a href="/companies/SA/data_collection/auth_for_client/">Selfassesment Data Collection</a>'),
    
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_create_name,
    'export_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_export_name,

    'template_tag': generate_template_tag_for_model(SelfemploymentIncomeAndExpensesDataCollection, pk_field=pk_field, show_id=False, exclude_fields=exclude_fields, include_fields=include_fields, keep_include_fields=keep_include_fields, show_others=show_others),
    'data_container': generate_data_container_table(SelfemploymentIncomeAndExpensesDataCollection, pk_field=pk_field, show_id=False, exclude_fields=exclude_fields, include_fields=include_fields, keep_include_fields=keep_include_fields, show_others=show_others),

    "counts": True,
    "selfassesment_data_collection_counts": True,
    "selfassesment_data_collection_row_count": get_selfassesment_data_collection_row_count().filter(tax_year=current_tax_year).count(),

    'frontend_data':{
      'all_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Data_Collection_viewall_url,
      'search_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Data_Collection_search_url,
      'update_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Data_Collection_update_url,
      'delete_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Data_Collection_delete_url,
      'model_fields': model_fields
    },

    'tax_years': SelfassesmentAccountSubmissionTaxYear.objects.all(),
    'current_tax_year': current_tax_year,

    "export_field_names": group_fields_by_uniqueness({
      "SelfemploymentIncomeAndExpensesDataCollection": get_field_names_with_label(SelfemploymentIncomeAndExpensesDataCollection),
    })
  }
  return render(request=request, template_name='companies/home.html', context=context)


def create_selfassesment_data_collection_for_client(request, utr=None):
  tax_year = SelfassesmentAccountSubmissionTaxYear.get_max_year()
  try:
      selfassesment = Selfassesment.objects.get(UTR=utr)
  except Selfassesment.DoesNotExist:
    messages.error(request, 'Invalid UTR or we do not have your info.')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_auth_name_for_client)
  
  context = {
    'page_title': 'Submit Income and Expense Data',
    'form_title': 'Submit Income And Expense Data',
    
    'has_url_args': True,
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_create_name_for_client,
    'client_url_arg': utr,
    
    'form': SelfemploymentIncomeAndExpensesDataCollectionCreationFormForClients(initial={
      'selfassesment': selfassesment,
      'tax_year': tax_year
      }),
    'submit_button_text': 'Save',
    'hide_submit_button': True,
    }

  try:
    existing_record = SelfemploymentIncomeAndExpensesDataCollection.objects.get(selfassesment=selfassesment, tax_year=tax_year)
    context['form'] = SelfemploymentIncomeAndExpensesDataCollectionCreationFormForClients(instance=existing_record)
    if existing_record.is_submitted:
      context['hide_submit_button'] = True
    else:
      context['hide_submit_button'] = False

    if request.method == 'POST':
      form = SelfemploymentIncomeAndExpensesDataCollectionCreationFormForClients(request.POST, instance=existing_record)

      if not existing_record.is_submitted and form.is_valid():
        context['form'] = form
        updated_data = form.save(commit=True)
        if updated_data.is_submitted:
          context['hide_submit_button'] = True
        messages.success(request, f'Your data is updated successfully at {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}.')
      else:
        messages.error(request, 'You have previously provided data with Ready to Submit marked true so you can not update data to update data please contact us.')
        # return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_auth_name_for_client)
  except SelfemploymentIncomeAndExpensesDataCollection.DoesNotExist:
    context['hide_submit_button'] = False
    if request.method == 'POST':
      form = SelfemploymentIncomeAndExpensesDataCollectionCreationFormForClients(request.POST)
      context['form'] = form
      
      try:
        selfassesment = Selfassesment.objects.get(UTR=utr)
      except Selfassesment.DoesNotExist:
        messages.error(request, 'Invalid UTR or we do not have your info.')
        return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_auth_name_for_client)
      
      if form.is_valid():
        # Create row in selfassesment account submission
        account_submission = get_object_or_None(SelfassesmentAccountSubmission, delete_duplicate=False, client_id=selfassesment, tax_year=tax_year)
        if not account_submission:
          slefassesment_account_submission_auto_row(request, selfassesment, tax_year)
        
        assesment = form.save(commit=False)
        assesment.tax_year = tax_year
        assesment.selfassesment = selfassesment
        assesment.save()

        messages.add_message(request, messages.SUCCESS, 'We recieved your data!')
        return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_auth_name_for_client)
      else:
        messages.error(request, f'Action failed due to invalid data!')
  return render(request, template_name='companies/create_without_auth.html', context=context)

def auth_selfassesment_data_collection_for_client(request):
  context = {
    'page_title': 'Auth Income and Expense Data collection',
    'form_title': 'Auth Income And Expense Data Collection',

    'has_url_args': False,
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_auth_name_for_client,
    'create_url_arg': None,

    'form': SelfemploymentIncomeAndExpensesDataCollectionAuthFormForClients(),
    'submit_button_text': 'Login',
  }
  if request.method=="POST":
    form = SelfemploymentIncomeAndExpensesDataCollectionAuthFormForClients(request.POST)
    context['form'] = form
    if form.is_valid():
      utr = form.cleaned_data.get('utr')
      try:
        selfassesment = Selfassesment.objects.get(UTR=utr)
        return redirect(to=URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_create_name_for_client, utr=utr)
      except Selfassesment.DoesNotExist:
        form.add_error('utr', 'Invalid UTR')
  return render(request, template_name='companies/create_without_auth.html', context=context)

@login_required
def create_selfassesment_data_collection(request):
  context = {
    **URLS,

    'page_title': 'Create Selfassesment Income and Expense data',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_home_name,
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_create_name,
    'form_title': 'Selfassesment Income And Expense Data Collection',
    'form': SelfemploymentIncomeAndExpensesDataCollectionCreationForm(initial={
      'selfassesment': None,
      'tax_year': SelfassesmentAccountSubmissionTaxYear.get_max_year()}
      )
  }

  if request.method == 'POST':
    form = SelfemploymentIncomeAndExpensesDataCollectionCreationForm(request.POST)
    context['form'] = form
    if form.is_valid():
      assesment = form.save(commit=False)

      selfassesment = assesment.selfassesment
      tax_year = assesment.tax_year
      existing_record = get_object_or_None(SelfemploymentIncomeAndExpensesDataCollection, delete_duplicate=False, return_all=True, selfassesment=selfassesment, tax_year=tax_year)
      if not existing_record:
        # Create row in selfassesment account submission
        account_submission = get_object_or_None(SelfassesmentAccountSubmission, delete_duplicate=False, client_id=selfassesment, tax_year=tax_year)
        if not account_submission:
          slefassesment_account_submission_auto_row(request, selfassesment, tax_year)
    
        assesment.save()
        
        messages.success(request, "Record created")
      else:
        messages.error(request, "There is an existing Record for the selected client and the current year")
    else:
      messages.error(request, f'Action failed due to invalid data!')
  return render(request, template_name='companies/create.html', context=context)

@login_required
def update_selfassesment_data_collection(request, data_id):
  context = {
    **URLS,
    'page_title': f'Update Collected Data',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_home_name,
    'id': data_id,
    'update_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_update_name,
    'form_title': 'Update Collected Data Form',
    'form': SelfemploymentIncomeAndExpensesDataCollectionUpdateForm()
  }

  try:
    record =  SelfemploymentIncomeAndExpensesDataCollection.objects.get(id=data_id)
    context['form'] = SelfemploymentIncomeAndExpensesDataCollectionUpdateForm(instance=record)
  except SelfemploymentIncomeAndExpensesDataCollection.DoesNotExist:
    messages.error(request, f'Collected Data having id {data_id} does not exists!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_home_name)
    raise Http404

  if request.method == 'POST':
    form = SelfemploymentIncomeAndExpensesDataCollectionUpdateForm(request.POST, instance=record)
    context['form'] = form
    if form.is_valid():
      collected_data = form.save()
      collected_data.save()
      messages.success(request, f'Collected Data has been updated having id {data_id}!')
    else:
      messages.error(request, f'Updating Collected Data having id {data_id} failed due to invalid data!')
  return render(request, template_name='companies/update.html', context=context)

@login_required
@allowed_for_superuser(
  message="Sorry! You are not authorized to delete this.",
  redirect_to=URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_update_name)
def delete_selfassesment_data_collection(request, data_id:int):
  context = {
    **URLS,
    'page_title': 'Selfassesment Income And Expense Data Collection Deletion',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_viewall_name,
    'id': data_id,
    'delete_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_delete_name,
    'form_title': "Selfassesment Income And Expense Data Delete Form",
    'form': SelfemploymentIncomeAndExpensesDataCollectionDeleteForm()
  }
  try:
    record =  SelfemploymentIncomeAndExpensesDataCollection.objects.get(id=data_id)
  except SelfemploymentIncomeAndExpensesDataCollection.DoesNotExist:
    messages.error(request, f'Selfassesment Collected Data record with id {data_id}, you are looking for does not exist!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_home_name)

  if request.method == 'POST':
    form = SelfemploymentIncomeAndExpensesDataCollectionDeleteForm(request.POST)
    context['form'] = form
    if form.is_valid():
      record.delete()
      messages.success(request, f'Selfassesment Collected Data has been deleted having id {data_id}!')
    else:
      messages.error(request, f'Selfassesment Collected Data deletion of id {data_id} failed!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_home_name)
  return render(request, template_name='companies/delete.html', context=context)

@login_required
def search_selfassesment_data_collection(request, limit:int=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    tax_year = request.GET.get('tax_year', None)
    if tax_year:
      try:
        tax_year = int(tax_year)
      except ValueError:
        tax_year = None

    if request.GET.get('tasks'):
      tasks = {
        "selfassesment_data_collection_row_count": get_selfassesment_data_collection_row_count(),
      }
      records = tasks.get(request.GET.get('tasks'), SelfemploymentIncomeAndExpensesDataCollection.objects.none())
      if tax_year:
        records = records.filter(tax_year=tax_year)
      records = records.order_by('-created_at')

      data = serialize(queryset=records, format='json')
      return HttpResponse(data, content_type='application/json')

    search_text = request.GET.get('q', '')
    if search_text.strip()=='':
      return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_viewall_name)
    records = db_search_SelfemploymentIncomeAndExpensesDataCollection(search_text, limit)
    if tax_year:
      records = records.filter(tax_year=tax_year)
    records = records.order_by("-created_at")

    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
def all_selfassesment_data_collection(request, limit:int=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    tax_year = request.GET.get('tax_year', None)
    if tax_year:
      try:
        tax_year = int(tax_year)
      except ValueError:
        tax_year = None
    
    records = db_all_SelfemploymentIncomeAndExpensesDataCollection(limit)
    if tax_year:
      records = records.filter(tax_year=tax_year)
    records = records.order_by("-created_at")

    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
@allowed_for_superuser(
  message="Sorry! You are not authorized to export this.",
  redirect_to=URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Data_Collection_home_name)
def export_selfassesment_data_collection(request):
  # get field names to export these are in '.' separated format for nested fields
  params = request.GET
  field_names = params.get('export_fields', None)
  if field_names:
    field_names = field_names.split(",")
  else:
    field_names = []

  tax_year_id = request.GET.get('tax_year', None)
  if tax_year_id:
    try:
      tax_year_id = int(tax_year_id)
    except ValueError:
      tax_year_id = None
  django_model = SelfemploymentIncomeAndExpensesDataCollection
  data_to_export = django_model.objects.all()
  if tax_year_id:
    data_to_export = data_to_export.filter(tax_year=tax_year_id)

  response = HttpResponse(
    content_type='text/csv',
    headers={'Content-Disposition': f'attachment; filename="selfassesment_{timezone.localtime()}.csv"'},
  )
  default_include_fields = []
  include_fields = field_names if len(field_names)>0 else default_include_fields
  exclude_fields = []
  fk_fields = {
    'selfassesment': SELFASSESMENT_FK_FIELDS_FOR_EXPORT,
    'tax_year': ['tax_year']
  }
  keep_include_fields = True
  show_others = (include_fields==default_include_fields)
  export_to_csv(
    django_model = django_model,
    write_to = response,
    include_fields = include_fields,
    exclude_fields = exclude_fields,
    keep_include_fields = keep_include_fields,
    show_others = show_others,
    fk_fields=fk_fields,
    records=data_to_export
    )
  return response



# =============================================================================================================
# =============================================================================================================
# SelfassesmentAccountSubmission
def get_selfassesment_account_submissions_where_status_PAID():
  return SelfassesmentAccountSubmission.objects.filter(payment_status="PAID")

def get_selfassesment_account_submissions_where_status_NOT_PAID():
  return SelfassesmentAccountSubmission.objects.filter(payment_status="NOT PAID")
  
def get_selfassesment_account_submissions_where_status_SUBMITTED_BUT_NOT_PAID():
  return SelfassesmentAccountSubmission.objects.filter(payment_status="NOT PAID", status="SUBMITTED")

def get_selfassesment_account_submissions_where_status_REQUEST():
  return SelfassesmentAccountSubmission.objects.filter(status="REQUEST")

def get_selfassesment_account_submissions_where_status_PRIORITY():
  return SelfassesmentAccountSubmission.objects.filter(status="PRIORITY")

def get_selfassesment_account_submissions_where_status_PROCESSING():
  return SelfassesmentAccountSubmission.objects.filter(status="PROCESSING")

def get_selfassesment_account_submissions_where_status_BOOK_APPOINTMENT():
  return SelfassesmentAccountSubmission.objects.filter(status="BOOK APPOINTMENT")

def get_selfassesment_account_submissions_where_status_READY_FOR_SUBMIT():
  return SelfassesmentAccountSubmission.objects.filter(status="READY FOR SUBMIT")

def get_selfassesment_account_submissions_where_status_WAITING_FOR_INFORMATION():
  return SelfassesmentAccountSubmission.objects.filter(status="WAITING FOR INFORMATION")

def get_selfassesment_account_submissions_where_status_WAITING_FOR_CONFIRMATION():
  return SelfassesmentAccountSubmission.objects.filter(status="WAITING FOR CONFIRMATION")

def get_selfassesment_account_submissions_where_status_SUBMITTED():
  return SelfassesmentAccountSubmission.objects.filter(status="SUBMITTED")

def get_selfassesment_account_submissions_where_status_NOT_ISSUED():
  return SelfassesmentAccountSubmission.objects.filter(status="NOT ISSUED")

def get_selfassesment_account_submissions_where_status_CLIENT_CLOSED():
  return SelfassesmentAccountSubmission.objects.filter(status="CLIENT CLOSED")

def get_selfassesment_account_submissions_where_status_ASSIGNED_TO_ME(user):
  return SelfassesmentAccountSubmission.objects.filter(assigned_to=user)

def get_selfassesment_account_submissions_where_status_NOT_ASSIGNED():
  return SelfassesmentAccountSubmission.objects.filter(assigned_to=None)

def get_selfassesment_account_submissions_where_data_collected(tax_year=None):
  if tax_year == None:
    tax_year = SelfassesmentAccountSubmissionTaxYear.get_max_year()
  collected_data_for_clients_for_current_year = SelfemploymentIncomeAndExpensesDataCollection.objects.filter(tax_year=tax_year)
  return SelfassesmentAccountSubmission.objects.filter(tax_year=tax_year, client_id__in=Subquery(collected_data_for_clients_for_current_year.values('selfassesment__pk')))


@login_required
def home_selfassesment_account_submission(request):
  current_tax_year = SelfassesmentAccountSubmissionTaxYear.get_max_year()
  pk_field = 'submission_id'
  include_fields = [
    "submission_id",
    "client_id",
    "request_date",
    "status",
    "appointment_date",
    "tax_year",
    "remarks",
    "submitted_by",
    "is_submitted",
    "is_data_collected",
    "prepared_by",
    "payment_status",
    "payment_method",
    "paid_amount",
    "unique_public_view_key",
    "assigned_to",
    "last_updated_by",
    "last_updated_on",
  ]
  exclude_fields = []
  keep_include_fields = True
  context = {
    **URLS,
    'caption': 'View Selfassesment Account Submission',
    'page_title': 'View Selfassesment Account Submission',
    
    # 'add_all_url': URL_NAMES_PREFIXED_WITH_APP_NAME.add_all_Selfassesment_to_Selfassesment_Account_Submission_name,
    # 'add_all_text': 'Add all Selfassesment to Selfassesment Account Submission',

    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_create_name,
    'export_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_export_name,

    'template_tag': generate_template_tag_for_model(SelfassesmentAccountSubmission, pk_field=pk_field, show_id=True, include_fields=include_fields, exclude_fields=exclude_fields, keep_include_fields=keep_include_fields),
    'data_container': generate_data_container_table(SelfassesmentAccountSubmission, pk_field=pk_field, show_id=True, include_fields=include_fields, exclude_fields=exclude_fields, keep_include_fields=keep_include_fields),

    "counts": True,
    "selfassesment_account_submission_counts": True,
    "selfassesment_account_submission_status_PAID": get_selfassesment_account_submissions_where_status_PAID().filter(tax_year=current_tax_year).count(),
    "selfassesment_account_submission_status_NOT_PAID": get_selfassesment_account_submissions_where_status_NOT_PAID().filter(tax_year=current_tax_year).count(),
    "selfassesment_account_submission_status_SUBMITTED_BUT_NOT_PAID": get_selfassesment_account_submissions_where_status_SUBMITTED_BUT_NOT_PAID().filter(tax_year=current_tax_year).count(),
    "selfassesment_account_submission_status_REQUEST": get_selfassesment_account_submissions_where_status_REQUEST().filter(tax_year=current_tax_year).count(),
    "selfassesment_account_submission_status_PRIORITY": get_selfassesment_account_submissions_where_status_PRIORITY().filter(tax_year=current_tax_year).count(),
    "selfassesment_account_submission_status_PROCESSING": get_selfassesment_account_submissions_where_status_PROCESSING().filter(tax_year=current_tax_year).count(),
    "selfassesment_account_submission_status_BOOK_APPOINTMENT": get_selfassesment_account_submissions_where_status_BOOK_APPOINTMENT().filter(tax_year=current_tax_year).count(),
    "selfassesment_account_submission_status_READY_FOR_SUBMIT": get_selfassesment_account_submissions_where_status_READY_FOR_SUBMIT().filter(tax_year=current_tax_year).count(),
    "selfassesment_account_submission_status_WAITING_FOR_INFORMATION": get_selfassesment_account_submissions_where_status_WAITING_FOR_INFORMATION().filter(tax_year=current_tax_year).count(),
    "selfassesment_account_submission_status_WAITING_FOR_CONFIRMATION": get_selfassesment_account_submissions_where_status_WAITING_FOR_CONFIRMATION().filter(tax_year=current_tax_year).count(),
    "selfassesment_account_submission_status_SUBMITTED": get_selfassesment_account_submissions_where_status_SUBMITTED().filter(tax_year=current_tax_year).count(),
    "selfassesment_account_submission_status_ASSIGNED_TO_ME": get_selfassesment_account_submissions_where_status_ASSIGNED_TO_ME(request.user).filter(tax_year=current_tax_year).count(),
    "selfassesment_account_submission_status_NOT_ASSIGNED": get_selfassesment_account_submissions_where_status_NOT_ASSIGNED().filter(tax_year=current_tax_year).count(),
    "selfassesment_account_submission_status_NOT_ISSUED": get_selfassesment_account_submissions_where_status_NOT_ISSUED().filter(tax_year=current_tax_year).count(),
    "selfassesment_account_submission_status_CLIENT_CLOSED": get_selfassesment_account_submissions_where_status_CLIENT_CLOSED().filter(tax_year=current_tax_year).count(),
    "selfassesment_account_submission_data_collected": get_selfassesment_account_submissions_where_data_collected(current_tax_year).count(),
    "selfassesment_account_submission__selfassesment_which_are_not_added_in_selfassesment_account_submission": get_selfassesment_account_submissions_where_data_collected(current_tax_year).count(),
    "selfassesment_not_added_in_selfassesment_account_submission": get_selfassesment_which_are_not_added_in_selfassesment_account_submission(tax_year=current_tax_year).count(),

    'frontend_data':{
      'all_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Account_Submission_viewall_url,
      'search_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Account_Submission_search_url,
      'update_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Account_Submission_update_url,
      'delete_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Account_Submission_delete_url,  
      'model_fields': get_field_names_from_model(SelfassesmentAccountSubmission)
    },

    'tax_years': SelfassesmentAccountSubmissionTaxYear.objects.all(),
    'current_tax_year': current_tax_year,

    "export_field_names": group_fields_by_uniqueness({
      "SelfassesmentAccountSubmission": get_field_names_with_label(SelfassesmentAccountSubmission),
    })
  }
  return render(request=request, template_name='companies/home.html', context=context)

@login_required
def view_selfassesment_account_submission(request):
  return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_home_name)

@login_required
def create_selfassesment_account_submission(request):
  context = {
    **URLS,

    'page_title': 'Create Selfassesment Account Submission',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_home_name,
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_create_name,
    'form_title': 'Selfassesment Account Submission Creation Form',
    'form': SelfassesmentAccountSubmissionCreationForm(initial={'submitted_by': request.user.user_id, 'tax_year': SelfassesmentAccountSubmissionTaxYear.get_max_year()})
  }

  if request.method == 'POST':
    form = SelfassesmentAccountSubmissionCreationForm(request.POST)
    context['form'] = form
    if form.is_valid():
      try:
        assesment = form.save()
        assesment.prepared_by = request.user
        assesment.set_defaults(request)
        assesment.save()
        messages.success(request, f'New Selfassesment Account Submission has been created with id {assesment.submission_id}!')
        context['form'] = SelfassesmentAccountSubmissionCreationForm(initial={'submitted_by': request.user.user_id})
      except IntegrityError:
        messages.error(request, f"Selfassesment Account Submission can't be updated because Client Name, Tax Year and Status is SUBMITTED is not unique!")
    else:
      messages.error(request, f'Action failed due to invalid data!')
  return render(request, template_name='companies/create.html', context=context)

@login_required
def update_selfassesment_account_submission(request, submission_id:int):
  hide_navbar = False
  if request.method=='GET':
    hide_navbar = request.GET.get('hide_navbar', False)

  context = {
    **URLS,
    'page_title': f'Update Selfassesment Account Submission',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_home_name,
    'id': submission_id,
    'update_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_update_name,
    'form_title': 'Selfassesment Account Submission Update Form',
    'form': SelfassesmentAccountSubmissionChangeForm(),
    'hide_navbar': hide_navbar
  }

  try:
    record =  SelfassesmentAccountSubmission.objects.get(submission_id=submission_id)
    currently_assigned_to = record.assigned_to
    context['form'] = SelfassesmentAccountSubmissionChangeForm(instance=record)
  except SelfassesmentAccountSubmission.DoesNotExist:
    messages.error(request, f'Selfassesment Account Submission having id {submission_id} does not exists!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_home_name)
    raise Http404

  # if record.status=="SUBMITTED" and not request.user.is_superuser:
  #   messages.error(request, f'You can not update the submission it is already submitted!')
  #   return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_home_name)

  if request.method == 'POST':
    form = SelfassesmentAccountSubmissionChangeForm(request.POST, instance=record)
    context['form'] = form
    if form.is_valid():
      try:
        assesment = form.save(commit=False)
        assesment.set_defaults(request)
        if assesment.status=="SUBMITTED" and assesment.submitted_by==None:
          form.add_error('submitted_by', 'Submitted By is required when Is Submitted is True')
          return render(request, template_name='companies/update.html', context=context)
        if assesment.status!="SUBMITTED" and assesment.submitted_by!=None:
          form.add_error('status', 'Status must be "SUBMITTED" to update Submitted by')
          return render(request, template_name='companies/update.html', context=context)
        if not assesment.assigned_to==currently_assigned_to and not request.user.is_superuser:
          messages.error(request, "Only admins can change Assigned to")
          return render(request, template_name='companies/update.html', context=context)
        assesment.save()
        messages.success(request, f'Selfassesment Account Submission has been updated having id {submission_id}!')
      except IntegrityError:
        messages.error(request, f"Selfassesment Account Submission can't be updated because Client Name, Tax Year and Status is SUBMITTED is not unique!")
    else:
      messages.error(request, f'Updating Selfassesment Account Submission having id {submission_id} failed due to invalid data!')
  return render(request, template_name='companies/update.html', context=context)

@login_required
@allowed_for_superuser(
  message="Sorry! You are not authorized to delete this.",
  redirect_to=URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_home_name)
def delete_selfassesment_account_submission(request, submission_id:int):
  context = {
    **URLS,
    'page_title': 'Delete Selfassesment Account Submission',
    'id': submission_id,
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_home_name,
    'delete_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_delete_name,
    'form_title': "Selfassesment Account Submission Delete Form",
    'form': SelfassesmentAccountSubmissionDeleteForm()
  }

  try:
    record = SelfassesmentAccountSubmission.objects.get(submission_id=submission_id)
  except SelfassesmentAccountSubmission.DoesNotExist:
    messages.error(request, f'Selfassesment Account Submission record with id {submission_id}, you are looking for does not exist!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_home_name)
  
  if request.method == 'POST':
    form = SelfassesmentAccountSubmissionDeleteForm(request.POST)
    context['form'] = form
    if form.is_valid():
      record.delete()
      messages.success(request, f'Selfassesment Account Submission has been deleted having id {submission_id}!')
    else:
      messages.error(request, f'Deletion of Selfassesment Account Submission having id {submission_id} failed!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_home_name)
  return render(request, template_name='companies/delete.html', context=context)

@login_required
def search_selfassesment_account_submission(request, limit: int=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    search_text = request.GET.get('q', '')
    submission_id = request.GET.get('pk', None)
    tax_year = request.GET.get('tax_year', None)
    if tax_year:
      try:
        tax_year = int(tax_year)
      except ValueError:
        tax_year = None
    else:
      tax_year = SelfassesmentAccountSubmissionTaxYear.get_max_year()

    if submission_id:
      error_message = {'error': 'The resource you are looking for does not exist'}
      error_response = HttpResponse(json.dumps(error_message), content_type='application/json', status=404)

      if not submission_id.isnumeric():
        return error_response

      try:
        submission_record = SelfassesmentAccountSubmission.objects.get(pk=submission_id)
      except SelfassesmentAccountSubmission.DoesNotExist:
        return error_response
      
      serialized_record = SelfassesmentAccountSubmissionSerializer(instance=submission_record)
      json_response = dump_model_to_json.render(serialized_record.data)
      return HttpResponse(json_response, content_type='application/json')


    # if tasks query paramter exists then return tasks
    if request.GET.get('tasks'):
      tasks = {
        "selfassesment_account_submission_status_PAID": get_selfassesment_account_submissions_where_status_PAID().filter(tax_year=tax_year),
        "selfassesment_account_submission_status_NOT_PAID": get_selfassesment_account_submissions_where_status_NOT_PAID().filter(tax_year=tax_year),
        "selfassesment_account_submission_status_SUBMITTED_BUT_NOT_PAID": get_selfassesment_account_submissions_where_status_SUBMITTED_BUT_NOT_PAID().filter(tax_year=tax_year),
        "selfassesment_account_submission_status_REQUEST": get_selfassesment_account_submissions_where_status_REQUEST().filter(tax_year=tax_year),
        "selfassesment_account_submission_status_PRIORITY": get_selfassesment_account_submissions_where_status_PRIORITY().filter(tax_year=tax_year),
        "selfassesment_account_submission_status_PROCESSING": get_selfassesment_account_submissions_where_status_PROCESSING().filter(tax_year=tax_year),
        "selfassesment_account_submission_status_BOOK_APPOINTMENT": get_selfassesment_account_submissions_where_status_BOOK_APPOINTMENT().filter(tax_year=tax_year),
        "selfassesment_account_submission_status_READY_FOR_SUBMIT": get_selfassesment_account_submissions_where_status_READY_FOR_SUBMIT().filter(tax_year=tax_year),
        "selfassesment_account_submission_status_WAITING_FOR_INFORMATION": get_selfassesment_account_submissions_where_status_WAITING_FOR_INFORMATION().filter(tax_year=tax_year),
        "selfassesment_account_submission_status_WAITING_FOR_CONFIRMATION": get_selfassesment_account_submissions_where_status_WAITING_FOR_CONFIRMATION().filter(tax_year=tax_year),
        "selfassesment_account_submission_status_SUBMITTED": get_selfassesment_account_submissions_where_status_SUBMITTED().filter(tax_year=tax_year),
        "selfassesment_account_submission_status_ASSIGNED_TO_ME": get_selfassesment_account_submissions_where_status_ASSIGNED_TO_ME(request.user).filter(tax_year=tax_year),
        "selfassesment_account_submission_status_NOT_ASSIGNED": get_selfassesment_account_submissions_where_status_NOT_ASSIGNED().filter(tax_year=tax_year),
        "selfassesment_account_submission_status_NOT_ISSUED": get_selfassesment_account_submissions_where_status_NOT_ISSUED().filter(tax_year=tax_year),
        "selfassesment_account_submission_status_CLIENT_CLOSED": get_selfassesment_account_submissions_where_status_CLIENT_CLOSED().filter(tax_year=tax_year),
        "selfassesment_account_submission_data_collected": get_selfassesment_account_submissions_where_data_collected(tax_year=tax_year),
        "selfassesment_not_added_in_selfassesment_account_submission": get_selfassesment_which_are_not_added_in_selfassesment_account_submission(tax_year=tax_year),
      }
      records = tasks.get(request.GET.get('tasks'), SelfassesmentAccountSubmission.objects.none())
      if tax_year:
        records = records.filter(tax_year=tax_year)

      data = serialize(queryset=records, format='json')
      return HttpResponse(data, content_type='application/json')

    if search_text.strip()=='':
      return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_viewall_name)
    records = db_search_SelfassesmentAccountSubmission(search_text, limit)
    if tax_year:
      records = records.filter(tax_year=tax_year)

    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
def all_selfassesment_account_submission(request, limit=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    tax_year = request.GET.get('tax_year', None)
    if tax_year:
      try:
        tax_year = int(tax_year)
      except ValueError:
        tax_year = None
    
    records = db_all_SelfassesmentAccountSubmission(limit)
    if tax_year:
      records = records.filter(tax_year=tax_year)
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

SELFASSESMENT_FK_FIELDS_TO_EXPORT = SELFASSESMENT_FK_FIELDS_FOR_EXPORT.copy()
SELFASSESMENT_FK_FIELDS_TO_EXPORT.remove('client_name')
@login_required
@allowed_for_superuser(
  message="Sorry! You are not authorized to export this.",
  redirect_to=URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_home_name)
def export_selfassesment_account_submission(request):
  # get field names to export these are in '.' separated format for nested fields
  params = request.GET
  field_names = params.get('export_fields', None)
  if field_names:
    field_names = field_names.split(",")
  else:
    field_names = []
  
  tax_year_id = request.GET.get('tax_year', None)
  if tax_year_id:
    try:
      tax_year_id = int(tax_year_id)
    except ValueError:
      tax_year_id = None
  django_model = SelfassesmentAccountSubmission
  data_to_export = django_model.objects.all()
  if tax_year_id:
    data_to_export = data_to_export.filter(tax_year=tax_year_id)
  
  response = HttpResponse(
    content_type='text/csv',
    headers={'Content-Disposition': f'attachment; filename="selfassesment_account_submimssion_{timezone.localtime()}.csv"'},
  )
  default_include_fields = []
  include_fields = field_names if len(field_names)>0 else default_include_fields
  exclude_fields = ['submission_id']
  fk_fields = {
    'client_id': [
        'client_name',
        'is_active',
        'start_date',
        'UTR',
        'HMRC_agent',
      ] + SELFASSESMENT_FK_FIELDS_TO_EXPORT
  }
  keep_include_fields = True
  show_others = (include_fields==default_include_fields)
  export_to_csv(
    django_model = django_model,
    write_to = response,
    include_fields = include_fields,
    exclude_fields = exclude_fields,
    keep_include_fields = keep_include_fields,
    show_others = show_others,
    fk_fields = fk_fields,
    records=data_to_export
    )
  return response

# add_all_selfassesment_to_selfassesment_account_submission_w_submission_year
@login_required
def add_all_selfassesment_to_selfassesment_account_submission_w_submission_year(request):
  context = {
    **URLS,
    'page_title': f'Add all Selfassesment to Selfassesment Account Submission',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_home_name,
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.add_all_Selfassesment_to_Selfassesment_Account_Submission_name,
    'form_title': 'Add all Selfassesment to Selfassesment Account Submission',
    'form': Add_All_Selfassesment_to_SelfassesmentAccountSubmission_Form(initial={'submitted_by': request.user, 'account_prepared_by': request.user})
  }
  if not request.user.is_superuser:
    messages.error(request, 'Only Superusers can use this feature!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_home_name)

  if request.method=='POST':
    form = Add_All_Selfassesment_to_SelfassesmentAccountSubmission_Form(data=request.POST)
    context['form'] = form
    if form.is_valid():
      submitted_by = form.cleaned_data.get('submitted_by')
      if submitted_by==None:
        form.cleaned_data['submitted_by'] = request.user

      all_Selfassesments = Selfassesment.objects.all()
      
      for assesment in all_Selfassesments:
        form.cleaned_data['client_id'] = assesment
        instance = SelfassesmentAccountSubmission(**form.cleaned_data)
        instance.set_defaults(request)
        if form.cleaned_data.get('prepared_by'):
          instance.prepared_by = form.cleaned_data.get('prepared_by')
        instance.save()
      messages.success(request, 'Added all Selfassesment to Selfassesment Account Submission!')
      return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Account_Submission_home_name)
  return render(request, 'companies/create.html', context=context)


# =============================================================================================================
# =============================================================================================================
# SelfassesmentTracker
selfassesment_tracker_home_redirect_page = URL_NAMES_PREFIXED_WITH_APP_NAME.Merged_Tracker_home_name

def get_selfassesment_trackers_where_tasks_customers_are_new():
  return SelfassesmentTracker.objects.filter(new_customer=True, is_completed=False)

def get_selfassesment_trackers_where_future_tasks_are_incomplete():
  return SelfassesmentTracker.objects.filter(is_completed=False, deadline__gt=timezone.localtime())

def get_selfassesment_trackers_where_todays_tasks_are_incomplete():
  return SelfassesmentTracker.objects.filter(is_completed=False, deadline=timezone.localtime())

def get_selfassesment_trackers_where_previous_tasks_are_incomplete():
  return SelfassesmentTracker.objects.filter(deadline__lt=timezone.localtime(), is_completed=False)

def get_selfassesment_trackers_where_tasks_has_issues():
  return SelfassesmentTracker.objects.filter(has_issue=True)

def get_selfassesment_trackers_where_tasks_assigned_to_user(user):
  return SelfassesmentTracker.objects.filter(assigned_to=user, is_completed=False)

@login_required
def home_selfassesment_tracker(request):
  pk_field = 'tracker_id'
  exclude_fields = set(['tracker_id', 'is_updated'])
  include_fields = ['tracker_id', 'client_id', 'job_description', 'deadline', 'remarks','is_completed', 'has_issue', 'complete_date', 'done_by', 'created_by','creation_date', 'issue_created_by']

  keep_include_fields = True
  context = {
    **URLS,
    'page_title': 'View Selfassesment Tracker',
    'caption': 'View Selfassesment Tracker',

    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Tracker_create_name,
    'export_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Tracker_export_name,

    'counts': True,
    'tracker_task_counts': True,
    'new_customers': get_selfassesment_trackers_where_tasks_customers_are_new().count(),
    'future_incomplete_tasks': get_selfassesment_trackers_where_future_tasks_are_incomplete().count(),
    'todays_incomplete_tasks': get_selfassesment_trackers_where_todays_tasks_are_incomplete().count(),
    'previous_incomplete_tasks': get_selfassesment_trackers_where_previous_tasks_are_incomplete().count(),
    'task_has_issue': get_selfassesment_trackers_where_tasks_has_issues().count(),
    'my_tasks': get_selfassesment_trackers_where_tasks_assigned_to_user(request.user).count(),

    'template_tag': generate_template_tag_for_model(SelfassesmentTracker, pk_field=pk_field, show_id=True, include_fields=include_fields, exclude_fields=exclude_fields, keep_include_fields=keep_include_fields),
    'data_container': generate_data_container_table(SelfassesmentTracker, pk_field=pk_field, show_id=True, include_fields=include_fields, exclude_fields=exclude_fields, keep_include_fields=keep_include_fields),

    'frontend_data':{
      'all_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Tracker_viewall_url,
      'search_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Tracker_search_url,
      'update_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Tracker_update_url,
      'delete_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Tracker_delete_url,  
      'model_fields': get_field_names_from_model(SelfassesmentTracker)
    },

    "export_field_names": group_fields_by_uniqueness({
      "SelfassesmentTracker": get_field_names_with_label(SelfassesmentTracker),
    })
  }
  return render(request=request, template_name='companies/home.html', context=context)

@login_required
def view_selfassesment_tracker(request):
  return redirect(selfassesment_tracker_home_redirect_page)

@login_required
def create_selfassesment_tracker(request):
  context = {
    **URLS,

    'page_title': 'Create Selfassesment Tracker',
    'view_url': selfassesment_tracker_home_redirect_page,
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Tracker_create_name,
    'form_title': 'Selfassesment Tracker Creation Form',
    'form': SelfassesmentTrackerCreationForm(initial={'created_by': request.user.user_id})
  }
  redirect_to = None

  if request.method == 'POST':
    redirect_to = request.POST.get('redirect_to', None)
    form = SelfassesmentTrackerCreationForm(request.POST, initial={'created_by': request.user.user_id})
    context['form'] = form
    if form.is_valid():
      assesment = form.save()
      assesment.created_by = request.user
      if not assesment.issue_created_by and assesment.has_issue:
        assesment.issue_created_by = request.user
      assesment.save()
      messages.success(request, f'New Selfassesment Tracker has been created with id {assesment.tracker_id}!')
      context['form'] = SelfassesmentTrackerCreationForm(initial={'created_by': request.user.user_id})
  try:
    if not redirect_to:
      redirect_to = request.GET.get('redirect_to')
    if redirect_to:
      return redirect(redirect_to, permanent=True)
  except NoReverseMatch:
    raise Http404
  return render(request, template_name='companies/create.html', context=context)


@login_required
def update_selfassesment_tracker(request, tracker_id:int):
  context = {
    **URLS,
    'page_title': f'Update Selfassesment Tracker',
    'view_url': selfassesment_tracker_home_redirect_page,
    'id': tracker_id,
    'update_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Tracker_update_name,
    'form_title': 'Selfassesment Tracker Update Form',
    'form': SelfassesmentTrackerChangeForm()
  }

  try:
    record =  SelfassesmentTracker.objects.get(tracker_id=tracker_id)
    context['form'] = SelfassesmentTrackerChangeForm(instance=record)
    if record.is_completed:
      messages.error(request, message=f"Task {tracker_id} is completed therefore can't be updated!")
      return redirect(selfassesment_tracker_home_redirect_page)
  except SelfassesmentTracker.DoesNotExist:
    messages.error(request, f'Selfassesment Tracker having id {tracker_id} does not exists!')
    return redirect(selfassesment_tracker_home_redirect_page)
    raise Http404

  if request.method == 'POST':
    form = SelfassesmentTrackerChangeForm(request.POST, instance=record)
    context['form'] = form
    if form.is_valid():
      assesment = form.save(commit=False)
      if not assesment.issue_created_by and assesment.has_issue:
        assesment.issue_created_by = request.user
      if form.cleaned_data.get('is_completed')==True:
        assesment.complete_date = timezone.localtime()
        assesment.done_by = request.user
        assesment.has_issue = False
      assesment.save()
      messages.success(request, f'Selfassesment Tracker has been updated having id {tracker_id}!')
      if assesment.is_completed:
        return redirect(selfassesment_tracker_home_redirect_page)
    else:
      messages.error(request, f'Updating Selfassesment Tracker having id {tracker_id} failed due to invalid data!')
  return render(request, template_name='companies/update.html', context=context)

@login_required
@allowed_for_superuser(
  message="Sorry! You are not authorized to delete this.",
  redirect_to=selfassesment_tracker_home_redirect_page)
def delete_selfassesment_tracker(request, tracker_id:int):
  context = {
    **URLS,
    'page_title': 'Delete Selfassesment Tracker',
    'view_url': selfassesment_tracker_home_redirect_page,
    'id': tracker_id,
    'delete_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Tracker_delete_name,
    'form_title': "Selfassesment Tracker Delete Form",
    'form': SelfassesmentTrackerDeleteForm()
  }

  try:
    record =  SelfassesmentTracker.objects.get(tracker_id=tracker_id)
  except SelfassesmentTracker.DoesNotExist:
    messages.error(request, f'Selfassesment Tracker record with id {tracker_id}, you are looking for does not exist!')
    return redirect(selfassesment_tracker_home_redirect_page)

  if request.method == 'POST':
    form = SelfassesmentTrackerDeleteForm(request.POST)
    context['form'] = form
    if form.is_valid():
      record.delete()
      messages.success(request, f'Selfassesment Tracker has been deleted having id {tracker_id}!')
    else:
      messages.error(request, f'Deletion of Selfassesment Tracker having id {tracker_id} failed')
    return redirect(selfassesment_tracker_home_redirect_page)
  return render(request, template_name='companies/delete.html', context=context)

@login_required
def search_selfassesment_tracker(request, limit: int=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    # get search text from url query parameter
    search_text = request.GET.get('q', '').strip()
    client_id = request.GET.get('client_id', None)

    # if tasks query paramter exists then return tasks
    if request.GET.get('tasks'):
      tasks = {
        'new_customers': get_selfassesment_trackers_where_tasks_customers_are_new(),
        'future_incomplete_tasks': get_selfassesment_trackers_where_future_tasks_are_incomplete(),
        'todays_incomplete_tasks': get_selfassesment_trackers_where_todays_tasks_are_incomplete(),
        'previous_incomplete_tasks': get_selfassesment_trackers_where_previous_tasks_are_incomplete(),
        'task_has_issue': get_selfassesment_trackers_where_tasks_has_issues(),
        'my_tasks': get_selfassesment_trackers_where_tasks_assigned_to_user(request.user)
      }
      records = tasks.get(request.GET.get('tasks'), [])
      records.order_by('deadline') # type: ignore
      data = serialize(queryset=records, format='json')
      return HttpResponse(data, content_type='application/json')
    if not client_id==None:
      records = SelfassesmentTracker.objects.filter(client_id=client_id, is_completed=False)
      records.order_by('deadline')
      data = serialize(queryset=records, format='json')
      return HttpResponse(data, content_type='application/json')
    
    # filter results using the search_text
    if not search_text:
      return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Tracker_viewall_name)
    
    records = db_search_SelfassesmentTracker(
      search_text=search_text,
      user_email=request.user.email,
      is_superuser=request.user.is_superuser,
      limit=limit)
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
def all_selfassesment_tracker(request, limit=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    records = db_all_SelfassesmentTracker(
      user_email=request.user.email,
      is_superuser=request.user.is_superuser,
      limit=limit)
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
def export_selfassesment_tracker(request):
  response = HttpResponse(
    content_type='text/csv; charset=utf-8',
    headers={'Content-Disposition': f'attachment; filename="selfassesment_tracker_{timezone.localtime()}.csv"'},
  )
  # get field names to export these are in '.' separated format for nested fields
  params = request.GET
  field_names = params.get('export_fields', None)
  if field_names:
    field_names = field_names.split(",")
  else:
    field_names = []
  
  default_include_fields = []
  include_fields = field_names if len(field_names)>0 else default_include_fields
  exclude_fields = set(['tracker_id', 'is_updated', 'creation_date'])
  fk_fields = {
    'client_id': SELFASSESMENT_FK_FIELDS_FOR_EXPORT
  }
  keep_include_fields = True
  show_others = (include_fields==default_include_fields)
  export_to_csv(
    django_model = SelfassesmentTracker,
    write_to = response,
    include_fields = include_fields,
    exclude_fields = exclude_fields,
    keep_include_fields = keep_include_fields,
    show_others = show_others,
    fk_fields = fk_fields
    )
  return response


# =============================================================================================================
# =============================================================================================================
# Limited

def get_limited_where_UTR_NOT_SET():
  return Limited.objects.filter(UTR=None)

def get_limited_where_COMPANY_AUTH_CODE_NOT_SET():
  return Limited.objects.filter(company_auth_code=None)

def get_limited_where_AGENT_NOT_ACTIVE():
  return Limited.objects.filter(HMRC_agent=False)

def get_limited_where_Client_IS_ACTIVE():
  return Limited.objects.filter(is_active=True)
def get_limited_where_Client_IS_INACTIVE():
  return Limited.objects.filter(is_active=False)

def get_limited_where_onboarding_tasks_status_Done():
  return Limited.objects.filter(client_id__in=LimitedOnboardingTasks.objects.filter(task_status='Done').values('client_id'))
def get_limited_where_onboarding_tasks_status_InProgress():
  return Limited.objects.filter(client_id__in=LimitedOnboardingTasks.objects.filter(task_status='InProgress').values('client_id'))
def get_limited_where_onboarding_tasks_status_NeedToDo():
  return Limited.objects.filter(client_id__in=LimitedOnboardingTasks.objects.filter(task_status='NeedToDo').values('client_id'))
def get_limited_where_onboarding_tasks_status_NotApplicable():
  return Limited.objects.filter(client_id__in=LimitedOnboardingTasks.objects.filter(task_status='NotApplicable').values('client_id'))


@login_required
def home_limited(request):
  pk_field = 'client_id'
  exclude_fields = []
  include_fields = [
    'client_rating',
    'client_name',
    'client_file_number',
    'direct_debit_amount',
    # 'all_onboarding_tasks',
    'onboarding_tasks__status__Done',
    'onboarding_tasks__status__In_Progress',
    'onboarding_tasks__status__Need_to_do',
    'onboarding_tasks__status__Not_Applicable',
    'is_active',
    'HMRC_agent',
    'is_payroll',
    'payment_method',
    'company_reg_number',
    'company_auth_code',
    'remarks',
    'director_phone_number',
    'director_email',
    'UTR',
    'NINO',
    "vat",
    "created_by",
    "date_of_registration"
  ]
  keep_include_fields = True
  show_others = False
  model_fields = get_field_names_from_model(Limited)
  model_fields.append('incomplete_tasks')
  # model_fields.append('all_onboarding_tasks')
  model_fields.append('onboarding_tasks__status__Done')
  model_fields.append('onboarding_tasks__status__In_Progress')
  model_fields.append('onboarding_tasks__status__Need_to_do')
  model_fields.append('onboarding_tasks__status__Not_Applicable')
  context = {
    **URLS,
    'caption': 'View Limited',
    'page_title': 'View Limited',

    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_create_name,
    'export_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_export_name,

    'template_tag': generate_template_tag_for_model(Limited, pk_field=pk_field, show_id=False, exclude_fields=exclude_fields, include_fields=include_fields, keep_include_fields=keep_include_fields, show_others=show_others),
    'data_container': generate_data_container_table(Limited, pk_field=pk_field, show_id=False, exclude_fields=exclude_fields, include_fields=include_fields, keep_include_fields=keep_include_fields, show_others=show_others),

    "counts": True,
    "limited_counts": True,
    "limited_UTR_NOT_SET": get_limited_where_UTR_NOT_SET().count(),
    "limited_COMPANY_AUTH_CODE_NOT_SET": get_limited_where_COMPANY_AUTH_CODE_NOT_SET().count(),
    "limited_AGENT_NOT_ACTIVE": get_limited_where_AGENT_NOT_ACTIVE().count(),
    "limited_Client_IS_ACTIVE": get_limited_where_Client_IS_ACTIVE().count(),
    "limited_Client_IS_INACTIVE": get_limited_where_Client_IS_INACTIVE().count(),
    "limited_Client_IS_INACTIVE": get_limited_where_Client_IS_INACTIVE().count(),
    "limited_where_onboarding_tasks_status_Done": get_limited_where_onboarding_tasks_status_Done().count(),
    "limited_where_onboarding_tasks_status_InProgress": get_limited_where_onboarding_tasks_status_InProgress().count(),
    "limited_where_onboarding_tasks_status_NeedToDo": get_limited_where_onboarding_tasks_status_NeedToDo().count(),
    "limited_where_onboarding_tasks_status_NotApplicable": get_limited_where_onboarding_tasks_status_NotApplicable().count(),

    'frontend_data':{
      'all_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_viewall_url,
      'search_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_search_url,
      'update_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_update_url,
      'delete_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_delete_url,  
      'model_fields': model_fields
    },

    "export_field_names": group_fields_by_uniqueness({
      "Limited": get_field_names_with_label(Limited),
    })
  }
  return render(request=request, template_name='companies/home.html', context=context)

@login_required
def view_limited(request):
  return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_home_name)

@login_required
def create_limited(request):
  context = {
    **URLS,
    'page_title': 'Create Limited',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_home_name,
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_create_name,
    'form_title': 'Register Limited Company Form',
    'form': LimitedCreationForm(initial={'client_file_number': Limited.get_next_file_number()})
  }

  if request.method == 'POST':
    form = LimitedCreationForm(request.POST)
    context['form'] = form
    if form.is_valid():
      limited = form.save()
      limited.set_defaults()
      limited.created_by = request.user
      limited.save()
      messages.success(request, f"New Limited has been created {limited}!")

      # Create record in Limited Submission Deadline Tracker
      submission = LimitedSubmissionDeadlineTracker()
      submission.client_id = limited
      submission.updated_by = request.user
      submission.save()
      messages.success(request, f'New Limited Submission has been created {submission}!')

      # Create record in Limited Confirmation Statement Tracker
      statement = LimitedConfirmationStatementTracker()
      statement.client_id = limited
      statement.set_defaults(request)
      messages.success(request, f'New Limited Confirmation Statement has been created {submission}!')

      # Create record in Limited VAT Tracker
      if limited.vat:
        for i in range(3):
          vat = LimitedVATTracker()
          vat.client_id = limited
          vat.updated_by = request.user
          vat.save()
          messages.success(request, f'New Limited VAT Tracker has been created {vat}')

      return redirect('companies:limited_onboarding_tasks', client_id=limited.client_id)

      # Previous behaviour after adding new company
      # context['form'] = LimitedCreationForm(initial={'client_file_number': Limited.get_next_file_number()})
  return render(request, template_name='companies/create.html', context=context)

@login_required
def get_details_limited(request, client_id=None):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    record = get_object_or_404(Limited, client_id=client_id)
    response = LimitedSerializer(instance=record).data
    return HttpResponse(json.dumps(response))
  raise Http404

@login_required
def update_limited(request, client_id:int):
  context = {
    **URLS,
    'page_title': f'Update Limited',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_home_name,
    'id': client_id,
    'update_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_update_name,
    'form_title': 'Limited Update Form',
    'form': LimitedChangeForm()
  }

  try:
    record = Limited.objects.get(client_id=client_id)
    current_is_active_value = record.is_active
    had_vat = bool(record.vat)
    context['form'] = LimitedChangeForm(instance=record)
  except Limited.DoesNotExist:
    messages.error(request, f'Limited Account having id {client_id} does not exists!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_home_name)

  if request.method == 'POST':
    form = LimitedChangeForm(request.POST, instance=record)
    context['form'] = form
    if form.is_valid():  
      # Prevent non admin users from updating active status
      if form.cleaned_data.get('is_active')!=current_is_active_value and not request.user.is_superuser:
        form.add_error('is_active', 'Only admins can change the active status.')
        messages.error(request, 'Update failed due to permission error.')
        return render(request, template_name='companies/update.html', context=context)

      assesment = form.save()
      messages.success(request, f'Limited has been updated having id {client_id}!')
      
      if not had_vat and assesment.vat:
        # Create record in Limited VAT Tracker
        for i in range(3):
          vat = LimitedVATTracker()
          vat.client_id = record
          vat.updated_by = request.user
          vat.save()
          messages.success(request, f'New Limited VAT Tracker has been created {vat}')
    else:
      messages.error(request, f'Updating Limited {client_id} failed due to invalid data!')
  return render(request, template_name='companies/update.html', context=context)

@login_required
@allowed_for_superuser(
  message="Sorry! You are not authorized to delete this.",
  redirect_to=URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_home_name)
def delete_limited(request, client_id:int):
  context = {
    **URLS,
    'page_title': 'Delete Limited',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_home_name,
    'id': client_id,
    'delete_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_delete_name,
    'form_title': "Limited Delete Form",
    'form': LimitedDeleteForm()
  }
  try:
    record =  Limited.objects.get(client_id=client_id)
  except Limited.DoesNotExist:
    messages.error(request, f'Limited record with id {client_id}, you are looking for does not exist!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_home_name)

  if request.method == 'POST':
    form = LimitedDeleteForm(request.POST)
    context['form'] = form
    if form.is_valid():
      record.delete()
      messages.success(request, f'Limited has been deleted having id {client_id}!')
    else:
      messages.error(request, f'Limited deletion of id {client_id} failed!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_home_name)
  return render(request, template_name='companies/delete.html', context=context)

@login_required
def search_limited(request, limit: int=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    search_text = request.GET.get('q', '')

    # if tasks query paramter exists then return tasks
    if request.GET.get('tasks'):
      tasks = {
        "limited_UTR_NOT_SET": get_limited_where_UTR_NOT_SET(),
        "limited_COMPANY_AUTH_CODE_NOT_SET": get_limited_where_COMPANY_AUTH_CODE_NOT_SET(),
        "limited_AGENT_NOT_ACTIVE": get_limited_where_AGENT_NOT_ACTIVE(),
        "limited_Client_IS_ACTIVE": get_limited_where_Client_IS_ACTIVE(),
        "limited_Client_IS_INACTIVE": get_limited_where_Client_IS_INACTIVE(),
        "limited_where_onboarding_tasks_status_Done": get_limited_where_onboarding_tasks_status_Done(),
        "limited_where_onboarding_tasks_status_InProgress": get_limited_where_onboarding_tasks_status_InProgress(),
        "limited_where_onboarding_tasks_status_NeedToDo": get_limited_where_onboarding_tasks_status_NeedToDo(),
        "limited_where_onboarding_tasks_status_NotApplicable": get_limited_where_onboarding_tasks_status_NotApplicable(),
      }
      records = tasks.get(request.GET.get('tasks'), [])
      data = serialize(queryset=records, format='json')
      return HttpResponse(data, content_type='application/json')

    if search_text.strip()=='':
      return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Tracker_viewall_name)
    records = db_search_Limited(search_text, limit)
    records = records.order_by("-client_file_number")
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
def all_limited(request, limit=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    records = db_all_Limited(limit)
    records = records.order_by("-client_file_number")
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
@allowed_for_superuser(
  message="Sorry! You are not authorized to export this.",
  redirect_to=URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_home_name)
def export_limited(request):
  response = HttpResponse(
    content_type='text/csv',
    headers={'Content-Disposition': f'attachment; filename="limited_{timezone.localtime()}.csv"'},
  )
  # get field names to export these are in '.' separated format for nested fields
  params = request.GET
  field_names = params.get('export_fields', None)
  if field_names:
    field_names = field_names.split(",")
  else:
    field_names = []
  
  default_include_fields = ['is_active', 'is_payroll', 'payment_method', 'direct_debit_amount', 'client_file_number', 'client_name', 'company_reg_number', 'company_auth_code', 'remarks', 'director_name', 'director_phone_number', 'director_email', 'UTR', 'NINO', 'HMRC_agent', 'vat']
  include_fields = field_names if len(field_names)>0 else default_include_fields
  
  exclude_fields = ['client_id',]
  keep_include_fields = True
  show_others = not(include_fields==default_include_fields)
  export_to_csv(
    django_model = Limited,
    write_to = response,
    include_fields = include_fields,
    exclude_fields = exclude_fields,
    keep_include_fields = keep_include_fields,
    show_others = show_others
    )
  return response



# =============================================================================================================
# =============================================================================================================
# LimitedOnboardingTasks
@csrf_exempt
def update_limited_onboarding_tasks(request, client_id:int):
  try:
    limited = Limited.objects.get(client_id=client_id)
  except Limited.DoesNotExist:
    messages.error(request, f'Limited record with id {client_id}, you are looking for does not exist!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_home_name)
  
  if request.method=='GET':  
    onboarding_tasks = OnboardingTask.objects.all()
    context = {
      **URLS,
      'page_title': 'Limited Onboarding Tasks',
      'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_home_name,
      'id': client_id,
      'update_url':  'companies:limited_onboarding_tasks',
      'form_title': f"{limited.client_name} onboarding tasks",
      
      'form': LimitedOnboardingForm(),
      'limited': limited,
      'task_status_choices': LimitedOnboardingTasks.task_status_choices,
    }
    
    limited_onboarding_tasks = []
    for task in onboarding_tasks:
      try:
        limited_onboarding_tasks.append(LimitedOnboardingTasks.objects.get(client_id=limited, task_id=task))
      except LimitedOnboardingTasks.DoesNotExist:
        task = LimitedOnboardingTasks(client_id=limited, task_id=task)
        task.save()
        limited_onboarding_tasks.append(task)

    context['limited_onboarding_tasks'] = limited_onboarding_tasks
    return render(request, template_name='companies/limited_onboarding_tasks.html', context=context)
  
  elif request.method=='POST':
    post_data = json.loads(request.body)
    task_id = post_data.get('task_id', None)
    status = post_data.get('task_status', None)
    note = post_data.get('note', None)
    
    try:
      task = OnboardingTask.objects.get(id=task_id)
    except OnboardingTask.DoesNotExist:
      return HttpResponse(f"Task for {task_id} not found!", status=400)
    
    try:
      onboarding_task_for_limited = LimitedOnboardingTasks.objects.get(client_id=client_id, task_id=task_id)
    except LimitedOnboardingTasks.DoesNotExist:
      onboarding_task_for_limited = LimitedOnboardingTasks()
    
    onboarding_task_for_limited.client_id = limited.pk
    onboarding_task_for_limited.task_id = task.pk
    
    if status!=None:
      onboarding_task_for_limited.task_status = status

    if note!=None:
      onboarding_task_for_limited.note = note
    
    onboarding_task_for_limited.save()
    return HttpResponse("Success", status=200)
  
  return HttpResponse("Client error", status=400)

@login_required
def search_limited_onboarding_tasks(request, limit: int=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    # get search text from url query parameter
    client_id = request.GET.get('client_id', None)
    task_lookup = request.GET.get('tasks', None)
    count_only = request.GET.get('count_only', None)

    # if tasks query paramter exists then return tasks
    if task_lookup:
      records = LimitedOnboardingTasks.objects.all()
      if client_id:
        records = records.filter(client_id=client_id)
      tasks = {
        'all_tasks': records,
        'status__Done': records.filter(task_status='Done'),
        'status__InProgress': records.filter(task_status='InProgress'),
        'status__NeedToDo': records.filter(task_status='NeedToDo'),
        'status__NotApplicable': records.filter(task_status='NotApplicable'),
      }

      if task_lookup=='__all__' and count_only!=None:
        for key in tasks:
          tasks[key] = tasks[key].count() # type: ignore
        return HttpResponse(json.dumps(tasks), content_type='application/json')

      records = tasks.get(task_lookup, [])
      if count_only != None:
        return HttpResponse(json.dumps({'count': records.count()}), content_type='application/json') # type: ignore
      data = serialize(queryset=records, format='json')
      return HttpResponse(data, content_type='application/json')
    
    data = serialize(queryset=[], format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404


# =============================================================================================================
# =============================================================================================================
# LimitedTracker
limited_tracker_home_redirect_page = URL_NAMES_PREFIXED_WITH_APP_NAME.Merged_Tracker_home_name

def get_limited_trackers_where_tasks_customers_are_new():
  return LimitedTracker.objects.filter(new_customer=True, is_completed=False)

def get_limited_trackers_where_future_tasks_are_incomplete():
  return LimitedTracker.objects.filter(is_completed=False, deadline__gt=timezone.localtime())

def get_limited_trackers_where_todays_tasks_are_incomplete():
  return LimitedTracker.objects.filter(is_completed=False, deadline=timezone.localtime())

def get_limited_trackers_where_previous_tasks_are_incomplete():
  return LimitedTracker.objects.filter(deadline__lt=timezone.localtime(), is_completed=False)

def get_limited_trackers_where_tasks_has_issues():
  return LimitedTracker.objects.filter(has_issue=True)

def get_limited_trackers_where_tasks_assigned_to_user(user):
  return LimitedTracker.objects.filter(assigned_to=user, is_completed=False)

@login_required
def home_limited_tracker(request):
  pk_field = 'tracker_id'
  exclude_fields = set(['tracker_id', 'is_updated'])
  include_fields = ['tracker_id', 'client_id', 'job_description', 'deadline', 'remarks','is_completed', 'has_issue', 'complete_date', 'done_by', 'created_by','creation_date', 'issue_created_by']
  fk_fields = {
      'created_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'issue_created_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'done_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'submitted_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'prepared_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'assigned_to': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'client_id': { 'details_url_without_argument': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_details_url, 'repr-format': HTML_Generator.Limited_client_id_repr_format, 'href-url':Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_update_url },
      'incomplete_tasks': { 'details_url_without_argument': '/companies/SATrc/search/?client_id=', 'repr-format': r'{length}'}
      }

  keep_include_fields = True
  context = {
    **URLS,
    'page_title': 'View Limited Tracker',
    'caption': 'View Limited Tracker',
    
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Tracker_create_name,
    'export_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Tracker_export_name,
    
    'counts': True,
    'tracker_task_counts': True,
    'new_customers': get_limited_trackers_where_tasks_customers_are_new().count(),
    'future_incomplete_tasks': get_limited_trackers_where_future_tasks_are_incomplete().count(),
    'todays_incomplete_tasks': get_limited_trackers_where_todays_tasks_are_incomplete().count(),
    'previous_incomplete_tasks': get_limited_trackers_where_previous_tasks_are_incomplete().count(),
    'task_has_issue': get_limited_trackers_where_tasks_has_issues().count(),
    'my_tasks': get_limited_trackers_where_tasks_assigned_to_user(request.user).count(),

    'template_tag': generate_template_tag_for_model(LimitedTracker, pk_field=pk_field, show_id=True, include_fields=include_fields, exclude_fields=exclude_fields, keep_include_fields=keep_include_fields, fk_fields=fk_fields),
    'data_container': generate_data_container_table(LimitedTracker, pk_field=pk_field, show_id=True, include_fields=include_fields, exclude_fields=exclude_fields, keep_include_fields=keep_include_fields),

    'frontend_data':{
      'all_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Tracker_viewall_url,
      'search_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Tracker_search_url,
      'update_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Tracker_update_url,
      'delete_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Tracker_delete_url,  
      'model_fields': get_field_names_from_model(LimitedTracker)
    },

    "export_field_names": group_fields_by_uniqueness({
      "LimitedTracker": get_field_names_with_label(LimitedTracker),
    })
  }
  return render(request=request, template_name='companies/home.html', context=context)

@login_required
def view_limited_tracker(request):
  return redirect(limited_tracker_home_redirect_page)

@login_required
def create_limited_tracker(request):
  context = {
    **URLS,

    'page_title': 'Create Limited Tracker',
    'view_url': limited_tracker_home_redirect_page,
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Tracker_create_name,
    'form_title': 'Limited Tracker Creation Form',
    'form': LimitedTrackerCreationForm(initial={'created_by': request.user.user_id})
  }
  redirect_to = None

  if request.method == 'POST':
    redirect_to = request.POST.get('redirect_to', None)
    form = LimitedTrackerCreationForm(request.POST, initial={'created_by': request.user.user_id})
    context['form'] = form
    if form.is_valid():
      assesment = form.save()
      assesment.created_by = request.user
      if not assesment.issue_created_by and assesment.has_issue:
        assesment.issue_created_by = request.user
      assesment.save()
      messages.success(request, f'New Limited Tracker has been created with id {assesment.tracker_id}!')
      context['form'] = LimitedTrackerCreationForm(initial={'created_by': request.user.user_id})

  try:
    if not redirect_to:
      redirect_to = request.GET.get('redirect_to', None)
    if redirect_to:
      return redirect(redirect_to)
  except NoReverseMatch:
    raise Http404
  return render(request, template_name='companies/create.html', context=context)

@login_required
def update_limited_tracker(request, tracker_id:int):
  context = {
    **URLS,
    'page_title': f'Update Limited Tracker',
    'view_url': limited_tracker_home_redirect_page,
    'id': tracker_id,
    'update_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Tracker_update_name,
    'form_title': 'Limited Tracker Update Form',
    'form': LimitedTrackerChangeForm()
  }

  try:
    record =  LimitedTracker.objects.get(tracker_id=tracker_id)
    context['form'] = LimitedTrackerChangeForm(instance=record)
    if record.is_completed:
      messages.error(request, message=f"Task {tracker_id} is completed therefore can't be updated!")
      return redirect(limited_tracker_home_redirect_page)
  except LimitedTracker.DoesNotExist:
    messages.error(request, f'Limited Tracker having id {tracker_id} does not exists!')
    return redirect(limited_tracker_home_redirect_page)
    raise Http404

  if request.method == 'POST':
    form = LimitedTrackerChangeForm(request.POST, instance=record)
    context['form'] = form
    if form.is_valid():
      assesment = form.save(commit=False)
      if not assesment.issue_created_by and assesment.has_issue:
        assesment.issue_created_by = request.user
      if form.cleaned_data.get('is_completed')==True:
        assesment.complete_date = timezone.localtime()
        assesment.done_by = request.user
        assesment.has_issue = False
      assesment.save()
      messages.success(request, f'Limited Tracker has been updated having id {tracker_id}!')
      if assesment.is_completed:
        return redirect(limited_tracker_home_redirect_page)
    else:
      messages.error(request, f'Updating Limited Tracker having id {tracker_id} failed due to invalid data!')
  return render(request, template_name='companies/update.html', context=context)

@login_required
@allowed_for_superuser(
  message="Sorry! You are not authorized to delete this.",
  redirect_to=URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Tracker_home_name)
def delete_limited_tracker(request, tracker_id:int):
  context = {
    **URLS,
    'page_title': 'Delete Limited Tracker',
    'view_url': limited_tracker_home_redirect_page,
    'id': tracker_id,
    'delete_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Tracker_delete_name,
    'form_title': "Limited Tracker Delete Form",
    'form': LimitedTrackerDeleteForm()
  }

  try:
    record =  LimitedTracker.objects.get(tracker_id=tracker_id)
  except LimitedTracker.DoesNotExist:
    messages.error(request, f'Limited Tracker record with id {tracker_id}, you are looking for does not exist!')
    return redirect(limited_tracker_home_redirect_page)

  if request.method == 'POST':
    form = LimitedTrackerDeleteForm(request.POST)
    context['form'] = form
    if form.is_valid():
      record.delete()
      messages.success(request, f'Limited Tracker has been deleted having id {tracker_id}!')
    else:
      messages.error(request, f'Deletion of Limited Tracker having id {tracker_id} failed')
    return redirect(limited_tracker_home_redirect_page)
  return render(request, template_name='companies/delete.html', context=context)

@login_required
def search_limited_tracker(request, limit: int=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    # get search text from url query parameter
    search_text = request.GET.get('q', '').strip()
    client_id = request.GET.get('client_id', None)

    # if tasks query paramter exists then return tasks
    if request.GET.get('tasks'):
      tasks = {
        'new_customers': LimitedTracker.objects.filter(new_customer=True),
        'future_incomplete_tasks': LimitedTracker.objects.filter(is_completed=False, deadline__gt=timezone.localtime()),
        'todays_incomplete_tasks': LimitedTracker.objects.filter(is_completed=False, deadline=timezone.localtime()),
        'previous_incomplete_tasks': LimitedTracker.objects.filter(deadline__lt=timezone.localtime(), is_completed=False),
        'task_has_issue': LimitedTracker.objects.filter(has_issue=True),
        'my_tasks': get_limited_trackers_where_tasks_assigned_to_user(request.user),
      }
      records = tasks.get(request.GET.get('tasks'), [])
      records.order_by('deadline') # type: ignore
      data = serialize(queryset=records, format='json')
      return HttpResponse(data, content_type='application/json')
    if not client_id==None:
      records = LimitedTracker.objects.filter(client_id=client_id, is_completed=False)
      records.order_by('deadline')
      data = serialize(queryset=records, format='json')
      return HttpResponse(data, content_type='application/json')
    
    # filter results using the search_text
    if not search_text:
      return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Tracker_viewall_name)
    
    records = db_search_LimitedTracker(
      search_text=search_text,
      user_email=request.user.email,
      is_superuser=request.user.is_superuser,
      limit=limit)
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
def all_limited_tracker(request, limit=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    records = db_all_LimitedTracker(
      user_email=request.user.email,
      is_superuser=request.user.is_superuser,
      limit=limit)
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
def export_limited_tracker(request):
  response = HttpResponse(
    content_type='text/csv; charset=utf-8',
    headers={'Content-Disposition': f'attachment; filename="limited_tracker_{timezone.localtime()}.csv"'},
  )
  # get field names to export these are in '.' separated format for nested fields
  params = request.GET
  field_names = params.get('export_fields', None)
  if field_names:
    field_names = field_names.split(",")
  else:
    field_names = []
  
  default_include_fields = []
  include_fields = field_names if len(field_names)>0 else default_include_fields
  exclude_fields = set(['tracker_id', 'is_updated', 'creation_date'])
  fk_fields = {
    'client_id': LIMITED_FK_FIELDS_FOR_EXPORT
  }
  keep_include_fields = True
  show_others = (include_fields==default_include_fields)
  export_to_csv(
    django_model = LimitedTracker,
    write_to = response,
    include_fields = include_fields,
    exclude_fields = exclude_fields,
    keep_include_fields = keep_include_fields,
    show_others = show_others,
    fk_fields = fk_fields
    )
  return response


# Limited Submission Deadline Tracker

# =============================================================================================================
# =============================================================================================================
# LimitedSubmissionDeadlineTracker
def get_limited_submissions_where_status_DOCUMENT_REQUESTED():
  return LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(status="DOCUMENT REQUESTED")

def get_limited_submissions_where_status_WAITING_FOR_INFORMATION():
  return LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(status="WAITING FOR INFORMATION")

def get_limited_submissions_where_status_DOCUMENT_RECEIVED():
  return LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(status="DOCUMENT RECEIVED")

def get_limited_submissions_where_status_PROCESSING():
  return LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(status="PROCESSING")

def get_limited_submissions_where_status_WAITING_FOR_CONFIRMATION():
  return LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(status="WAITING FOR CONFIRMATION")

def get_limited_submissions_where_status_COMPLETED():
  return LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(status="COMPLETED")

def get_limited_submissions_where_deadline_not_set():
  return LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(HMRC_deadline = None)

def get_limited_submissions_where_company_house_deadline_missed_of_active_clients():
  return LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(HMRC_deadline__lt = timezone.now(), is_submitted=False, client_id__is_active=True)

def get_limited_submissions_where_company_house_deadline_missed_of_inactive_clients():
  return LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(HMRC_deadline__lt = timezone.now(), is_submitted=False, client_id__is_active=False)

def get_limited_submissions_where_HMRC_deadline_missed():
  return LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(our_deadline__lt = timezone.now(), is_submitted_hmrc=False)

def get_limited_submissions_where_period_end(limit=-1):
  records = LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(period__lt = timezone.now(), is_submitted=False)
  return records

def get_limited_submissions_where_payment_status_NOT_PAID(limit=-1):
  records = LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(payment_status="NOT PAID")
  return records

def get_limited_submissions_where_payment_status_PAID(limit=-1):
  records = LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(payment_status="PAID")
  return records

def get_limited_submissions_where_payment_status_INVOICE_SENT(limit=-1):
  records = LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(payment_status="INVOICE SENT")
  return records


def get_this_month_start_end():
  current_date = date.today()
  _, number_of_days = calendar.monthrange(year=current_date.year, month=current_date.month)
  current_month_start_date = date(year=current_date.year, month=current_date.month, day=1)
  current_month_end_date = date(year=current_date.year, month=current_date.month, day=number_of_days)
  return current_month_start_date, current_month_end_date

def get_limited_submissions_where_HMRC_deadline_this_month(limit=-1):
  start, end = get_this_month_start_end()
  records = LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(HMRC_deadline__gte=start, HMRC_deadline__lte=end)
  return records

def get_limited_submissions_where_HMRC_deadline_this_month_and_submitted(limit=-1):
  start, end = get_this_month_start_end()
  records = LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(HMRC_deadline__gte=start, HMRC_deadline__lte=end, is_submitted=True)
  return records

def get_limited_submissions_where_assigned_to_me(user):
  records = LimitedSubmissionDeadlineTracker.objects.filter(assigned_to=user).exclude(is_submitted=True, is_submitted_hmrc=True)
  return records



@login_required
def home_limited_submission_deadline_tracker(request):
  pk_field = 'submission_id'
  exclude_fields = []
  field_ordering = ['client_id', 'file_#', 'reg_num', 'status', 'assigned_to', 'period_start_date', 'period', 'remarks', 'HMRC_deadline', 'is_submitted', 'submitted_by', 'submission_date', 'our_deadline', 'is_submitted_hmrc', 'submitted_by_hmrc', 'submission_date_hmrc', 'is_documents_uploaded', ]
  model_fields = get_field_names_from_model(LimitedSubmissionDeadlineTracker)
  model_fields.append('reg_num')
  model_fields.append('file_#')
  keep_include_fields = False
  fk_fields = {
      'assigned_to': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'updated_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'submitted_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'submitted_by_hmrc': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'client_id': { 'details_url_without_argument': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_details_url, 'repr-format': HTML_Generator.Limited_client_id_repr_format, 'href-url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_update_url,},
      'reg_num': { 'details_url_without_argument': '/companies/LTD/details/', 'repr-format': r'{company_reg_number}', 'data-field': 'fields.client_id'},
      'file_#': { 'details_url_without_argument': '/companies/LTD/details/', 'repr-format': r'{client_file_number}', 'data-field': 'fields.client_id'},
      }
  context = {
    **URLS,
    'caption': 'View Limited Submission Deadline Tracker',
    'page_title': 'View Limited Submission Deadline Tracker',
    
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_create_name,
    'export_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_export_name,

    'counts': True,
    'limited_submission_counts': True,
    'submission_deadline_not_set': get_limited_submissions_where_deadline_not_set().count(),
    'submission_company_house_deadline_missed_of_active_clients': get_limited_submissions_where_company_house_deadline_missed_of_active_clients().count(),
    'submission_company_house_deadline_missed_of_inactive_clients': get_limited_submissions_where_company_house_deadline_missed_of_inactive_clients().count(),
    'submission_HMRC_deadline_missed': get_limited_submissions_where_HMRC_deadline_missed().count(),
    'submission_period_ended': get_limited_submissions_where_period_end().count(),
    'limited_submissions_status_DOCUMENT_REQUESTED': get_limited_submissions_where_status_DOCUMENT_REQUESTED().count(),
    'limited_submissions_status_WAITING_FOR_INFORMATION': get_limited_submissions_where_status_WAITING_FOR_INFORMATION().count(),
    'limited_submissions_status_DOCUMENT_RECEIVED': get_limited_submissions_where_status_DOCUMENT_RECEIVED().count(),
    'limited_submissions_status_PROCESSING': get_limited_submissions_where_status_PROCESSING().count(),
    'limited_submissions_status_WAITING_FOR_CONFIRMATION': get_limited_submissions_where_status_WAITING_FOR_CONFIRMATION().count(),
    'limited_submissions_status_COMPLETED': get_limited_submissions_where_status_COMPLETED().count(),
    'limited_submissions_payment_status_NOT_PAID': get_limited_submissions_where_payment_status_NOT_PAID().count(),
    'limited_submissions_payment_status_PAID': get_limited_submissions_where_payment_status_PAID().count(),
    'limited_submissions_payment_status_INVOICE_SENT': get_limited_submissions_where_payment_status_INVOICE_SENT().count(),
    'limited_submission_where_HMRC_deadline_this_month': get_limited_submissions_where_HMRC_deadline_this_month().count(),
    'limited_submission_where_HMRC_deadline_this_month_and_submitted': get_limited_submissions_where_HMRC_deadline_this_month_and_submitted().count(),
    'limited_submission_where_assigned_to_me': get_limited_submissions_where_assigned_to_me(request.user).count(),

    'template_tag': generate_template_tag_for_model(LimitedSubmissionDeadlineTracker, show_id=False, pk_field=pk_field, exclude_fields=exclude_fields, keep_include_fields=keep_include_fields, ordering=field_ordering, fk_fields=fk_fields),
    'data_container': generate_data_container_table(LimitedSubmissionDeadlineTracker, show_id=False, pk_field=pk_field, exclude_fields=exclude_fields, keep_include_fields=keep_include_fields, ordering=field_ordering),

    'frontend_data':{
      'all_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Submission_Deadline_Tracker_viewall_url,
      'search_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Submission_Deadline_Tracker_search_url,
      'update_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Submission_Deadline_Tracker_update_url,
      'delete_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Submission_Deadline_Tracker_delete_url,  
      'model_fields': model_fields
    },

    "export_field_names": group_fields_by_uniqueness({
      "LimitedSubmissionDeadlineTracker": get_field_names_with_label(LimitedSubmissionDeadlineTracker),
    })
  }
  return render(request=request, template_name='companies/home.html', context=context)

@login_required
def view_limited_submission_deadline_tracker(request):
  return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_home_name)

@login_required
def create_limited_submission_deadline_tracker(request):
  context = {
    **URLS,

    'page_title': 'Create Limited Submission Deadline Tracker',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_home_name,
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_create_name,
    'form_title': 'Limited Submission Deadline Tracker Creation Form',
    'form': LimitedSubmissionDeadlineTrackerCreationForm()
  }

  if request.method == 'POST':
    form = LimitedSubmissionDeadlineTrackerCreationForm(request.POST)
    context['form'] = form
    if form.is_valid():
      assesment = form.save()
      assesment.set_defaults(request)
      assesment.save()
      messages.success(request, f'New Limited Submission Deadline Tracker has been created with id {assesment.submission_id}!')
      context['form'] = LimitedSubmissionDeadlineTrackerCreationForm()
    else:
      messages.error(request, f'Action failed due to invalid data!')
  return render(request, template_name='companies/create.html', context=context)

@login_required
def update_limited_submission_deadline_tracker(request, submission_id:int):
  context = {
    **URLS,
    'page_title': f'Update Limited Submission Deadline Tracker',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_home_name,
    'id': submission_id,
    'update_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_update_name,
    'form_title': 'Limited Submission Deadline Tracker Update Form',
    'form': LimitedSubmissionDeadlineTrackerChangeForm()
  }

  try:
    record =  LimitedSubmissionDeadlineTracker.objects.get(submission_id=submission_id)
    if (record.is_submitted and record.is_submitted_hmrc) and not request.user.is_superuser:
      messages.error(request, message=f"Limited Submission Deadline Tracker {submission_id} is submitted therefore can't be updated!")
      return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_home_name)
    context['form'] = LimitedSubmissionDeadlineTrackerChangeForm(instance=record)
  except LimitedSubmissionDeadlineTracker.DoesNotExist:
    messages.error(request, f'Limited Submission Deadline Tracker having id {submission_id} does not exist!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_home_name)

  if request.method == 'POST':
    form = LimitedSubmissionDeadlineTrackerChangeForm(request.POST, instance=record)
    context['form'] = form

    new_assigned_to = form.data.get('assigned_to')
    old_assigned_to = str(record.assigned_to.pk) if record.assigned_to else None
    if not request.user.is_superuser and (new_assigned_to != old_assigned_to):
      form.add_error("assigned_to", "Only admins can update this field!")
      messages.error(request, "Update failed due to permission error")
      return render(request, template_name='companies/update.html', context=context)

    if form.is_valid():
      assesment = form.save(commit=False)

      # To submit the first record of a client require Period Start and Period End
      first_row_for_current_client = LimitedSubmissionDeadlineTracker.objects.filter(client_id=record.client_id).order_by('pk').first()
      if first_row_for_current_client==record and assesment.is_submitted==True and assesment.is_submitted_hmrc:
        if not form.cleaned_data.get('period_start_date'):
          form.add_error('period_start_date', 'This is the first record of this client therefore this field is required.')
        if not form.cleaned_data.get('period'):
          form.add_error('period', 'This is the first record of this client therefore this field is required.')
        if not form.is_valid():
          return render(request, template_name='companies/update.html', context=context)

      assesment.set_defaults(request)
      context['form'] = LimitedSubmissionDeadlineTrackerChangeForm(instance=assesment)
      messages.success(request, f'Limited Submission Deadline Tracker has been updated having id {submission_id}!')

      if assesment.is_submitted and not assesment.submitted_by:
        assesment.submitted_by = request.user
        assesment.save()
      else:
        assesment.submitted_by = None
        assesment.save()

      if assesment.is_submitted_hmrc and not assesment.submitted_by_hmrc:
        assesment.submitted_by_hmrc = request.user
        assesment.save()
      else:
        assesment.submitted_by_hmrc = None
        assesment.save()
      
      if assesment.charged_amount!=None and assesment.received_amount!=None:
        assesment.balance_amount = assesment.received_amount - assesment.charged_amount
        assesment.save()

      # Create new record for next year
      d = assesment.period_start_date
      if d == None:
        d = date.today()
      # Check if record already exists for next year
      does_newer_record_already_exist = LimitedSubmissionDeadlineTracker.objects.filter(client_id=assesment.client_id, period_start_date__gt=d).exists()
      if (assesment.is_submitted and assesment.is_submitted_hmrc) and not does_newer_record_already_exist:
        new_assesment = LimitedSubmissionDeadlineTracker()
        new_assesment.client_id = assesment.client_id
        new_assesment.updated_by = request.user
        new_assesment.HMRC_deadline = assesment.HMRC_deadline + relativedelta(years=1) # Company House deadline
        new_assesment.our_deadline = assesment.our_deadline + relativedelta(years=1) # HMRC Deadline
        new_assesment.period_start_date = assesment.period + relativedelta(days=1) # Period Start
        new_assesment.period = assesment.period + relativedelta(years=1) # Period End
        new_assesment.save()
        messages.success(request, f'New Limited Submission Deadline Tracker has been created {new_assesment}')
        return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_home_name)
    else:
      messages.error(request, f'Updating Limited Submission Deadline Tracker having id {submission_id} failed due to invalid data!')
  return render(request, template_name='companies/update.html', context=context)

@login_required
@allowed_for_superuser(
  message="Sorry! You are not authorized to delete this.",
  redirect_to=URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_home_name)
def delete_limited_submission_deadline_tracker(request, submission_id:int):
  context = {
    **URLS,
    'page_title': 'Delete Limited Submission Deadline Tracker',
    'id': submission_id,
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_home_name,
    'delete_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_delete_name,
    'form_title': "Limited Submission Deadline Tracker Delete Form",
    'form': LimitedSubmissionDeadlineTrackerDeleteForm()
  }

  try:
    record = LimitedSubmissionDeadlineTracker.objects.get(submission_id=submission_id)
  except LimitedSubmissionDeadlineTracker.DoesNotExist:
    messages.error(request, f'Limited Submission Deadline Tracker record with id {submission_id}, you are looking for does not exist!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_home_name)
  
  if request.method == 'POST':
    form = LimitedSubmissionDeadlineTrackerDeleteForm(request.POST)
    context['form'] = form
    if form.is_valid():
      record.delete()
      messages.success(request, f'Limited Submission Deadline Tracker has been deleted having id {submission_id}!')
    else:
      messages.error(request, f'Deletion of Limited Submission Deadline Tracker having id {submission_id} failed!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_home_name)
  return render(request, template_name='companies/delete.html', context=context)

@login_required
def search_limited_submission_deadline_tracker(request, limit: int=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    # get search text from url query parameter
    search_text = request.GET.get('q', '').strip()
    tasks_key = request.GET.get('tasks')

    # if tasks query paramter exists then return tasks
    if tasks_key:
      tasks = {
        'submission_deadline_not_set': get_limited_submissions_where_deadline_not_set(),
        'submission_company_house_deadline_missed_of_active_clients': get_limited_submissions_where_company_house_deadline_missed_of_active_clients(),
        'submission_company_house_deadline_missed_of_inactive_clients': get_limited_submissions_where_company_house_deadline_missed_of_inactive_clients(),
        'submission_HMRC_deadline_missed': get_limited_submissions_where_HMRC_deadline_missed(),
        'submission_period_ended': get_limited_submissions_where_period_end(),
        'limited_submissions_status_DOCUMENT_REQUESTED': get_limited_submissions_where_status_DOCUMENT_REQUESTED(),
        'limited_submissions_status_WAITING_FOR_INFORMATION': get_limited_submissions_where_status_WAITING_FOR_INFORMATION(),
        'limited_submissions_status_DOCUMENT_RECEIVED': get_limited_submissions_where_status_DOCUMENT_RECEIVED(),
        'limited_submissions_status_PROCESSING': get_limited_submissions_where_status_PROCESSING(),
        'limited_submissions_status_WAITING_FOR_CONFIRMATION': get_limited_submissions_where_status_WAITING_FOR_CONFIRMATION(),
        'limited_submissions_status_COMPLETED': get_limited_submissions_where_status_COMPLETED(),
        'limited_submissions_payment_status_NOT_PAID': get_limited_submissions_where_payment_status_NOT_PAID(),
        'limited_submissions_payment_status_PAID': get_limited_submissions_where_payment_status_PAID(),
        'limited_submissions_payment_status_INVOICE_SENT': get_limited_submissions_where_payment_status_INVOICE_SENT(),
        'limited_submission_where_HMRC_deadline_this_month': get_limited_submissions_where_HMRC_deadline_this_month(),
        'limited_submission_where_HMRC_deadline_this_month_and_submitted': get_limited_submissions_where_HMRC_deadline_this_month_and_submitted(),
        'limited_submission_where_assigned_to_me': get_limited_submissions_where_assigned_to_me(request.user),
      }
      records = tasks.get(tasks_key, [])
      data = serialize(queryset=records, format='json')
      return HttpResponse(data, content_type='application/json')
    
    # filter results using the search_text
    if search_text.strip()=='':
      return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_viewall_name)
    records = db_search_LimitedSubmissionDeadlineTracker(search_text, limit)
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
def all_limited_submission_deadline_tracker(request, limit=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    records = db_all_LimitedSubmissionDeadlineTracker(limit)
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
@allowed_for_superuser(
  message="Sorry! You are not authorized to export this.",
  redirect_to=URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Submission_Deadline_Tracker_home_name)
def export_limited_submission_deadline_tracker(request):
  response = HttpResponse(
    content_type='text/csv',
    headers={'Content-Disposition': f'attachment; filename="limited_submission_deadline_tracker_{timezone.localtime()}.csv"'},
  )
  # get field names to export these are in '.' separated format for nested fields
  params = request.GET
  field_names = params.get('export_fields', None)
  if field_names:
    field_names = field_names.split(",")
  else:
    field_names = []
  
  default_include_fields = []
  include_fields = field_names if len(field_names)>0 else default_include_fields
  exclude_fields = ['submission_id']
  fk_fields = {
    'client_id': LIMITED_FK_FIELDS_FOR_EXPORT
  }
  keep_include_fields = False
  show_others = (include_fields==default_include_fields)
  export_to_csv(
    django_model = LimitedSubmissionDeadlineTracker,
    write_to = response,
    include_fields = include_fields,
    exclude_fields = exclude_fields,
    keep_include_fields = keep_include_fields,
    show_others = show_others,
    fk_fields = fk_fields
    )
  return response

@login_required
def info_limited_submission_deadline_tracker(request):
  fields_metadata = []
  for field in LimitedSubmissionDeadlineTracker._meta.fields:
    field_meta = model_field_to_form_meta(field)
    if field_meta:
      fields_metadata.append(field_meta)
  return HttpResponse(json.dumps(fields_metadata))

# =============================================================================================================
# =============================================================================================================
# LimitedVATTracker
def get_limited_vats_where_deadline_not_set():
  return LimitedVATTracker.objects.filter(HMRC_deadline = None)

def get_limited_vats_where_deadline_missed():
  return LimitedVATTracker.objects.filter(HMRC_deadline__lt = timezone.now(), is_submitted=False)

def get_limited_vats_where_period_difference_more_than_3months():
  return LimitedVATTracker.objects.annotate(
  diff=ExpressionWrapper(F('period_end') - F('period_start'), 
  output_field=DurationField())).filter(diff__gte=timedelta(90), is_submitted=False)


@login_required
def home_limited_vat_tracker(request):
  pk_field = 'vat_id'
  exclude_fields = []
  field_ordering = ['client_id', 'period_start', 'period_end', 'HMRC_deadline', 'remarks',]
  keep_include_fields = True
  fk_fields = {
      'updated_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'client_id': { 'details_url_without_argument': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_details_url, 'repr-format': HTML_Generator.Limited_client_id_repr_format, 'href-url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_update_url,},
      }
  context = {
    **URLS,
    'caption': 'View VAT Tracker',
    'page_title': 'View VAT Tracker',
    
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_create_name,
    'export_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_export_name,

    'counts': True,
    'limited_vat_counts': True,
    'submission_deadline_not_set': get_limited_vats_where_deadline_not_set().count(),
    'submission_vat_deadline_missed': get_limited_vats_where_deadline_missed().count(),
    'period_diff_gt_3months': get_limited_vats_where_period_difference_more_than_3months().count(),

    'template_tag': generate_template_tag_for_model(LimitedVATTracker, pk_field=pk_field, show_id=False, ordering=field_ordering, fk_fields=fk_fields),
    'data_container': generate_data_container_table(LimitedVATTracker, pk_field=pk_field, show_id=False, ordering=field_ordering),

    'frontend_data':{
      'all_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_VAT_Tracker_viewall_url,
      'search_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_VAT_Tracker_search_url,
      'update_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_VAT_Tracker_update_url,
      'delete_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_VAT_Tracker_delete_url,  
      'model_fields': get_field_names_from_model(LimitedVATTracker)
    },
    
    "export_field_names": group_fields_by_uniqueness({
      "LimitedVATTracker": get_field_names_with_label(LimitedVATTracker),
    })
  }
  return render(request=request, template_name='companies/home.html', context=context)

@login_required
def view_limited_vat_tracker(request):
  return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_home_name)

@login_required
def create_limited_vat_tracker(request):
  context = {
    **URLS,

    'page_title': 'Create Limited VAT Tracker',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_home_name,
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_create_name,
    'form_title': 'Limited VAT Tracker Creation Form',
    'form': LimitedVATTrackerCreationForm()
  }

  if request.method == 'POST':
    form = LimitedVATTrackerCreationForm(request.POST)
    context['form'] = form
    if form.is_valid():
      assesment = form.save()
      assesment.set_defaults(request)
      assesment.save()
      messages.success(request, f'New Limited VAT Tracker has been created with id {assesment.vat_id}!')
      context['form'] = LimitedVATTrackerCreationForm()
    else:
      messages.error(request, f'Action failed due to invalid data!')
  return render(request, template_name='companies/create.html', context=context)

@login_required
def update_limited_vat_tracker(request, vat_id:int):
  context = {
    **URLS,
    'page_title': f'Update Limited VAT Tracker',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_home_name,
    'id': vat_id,
    'update_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_update_name,
    'form_title': 'Limited VAT Tracker Update Form',
    'form': LimitedVATTrackerChangeForm()
  }

  try:
    record =  LimitedVATTracker.objects.get(vat_id=vat_id)
    if record.is_submitted:
      messages.error(request, message=f"Limited VAT Tracker {vat_id} is submitted therefore can't be updated!")
      return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_home_name)
    context['form'] = LimitedVATTrackerChangeForm(instance=record)
  except LimitedVATTracker.DoesNotExist:
    messages.error(request, f'Limited VAT Tracker having id {vat_id} does not exists!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_home_name)
    raise Http404

  if request.method == 'POST':
    form = LimitedVATTrackerChangeForm(request.POST, instance=record)
    context['form'] = form
    if form.is_valid():
      assesment = form.save(commit=False)
      assesment.set_defaults(request)
      assesment.save()
      
      # Create new record for next year
      d = assesment.period_start
      if d == None:
        d = date.today()
      # Check if record already exists for next year
      does_newer_record_already_exist = LimitedVATTracker.objects.filter(client_id=assesment.client_id, period_start__gt=d).exists()
      # Create Limited VAT Tracker
      if assesment.is_submitted and not does_newer_record_already_exist:
        vat = LimitedVATTracker()
        vat.client_id = assesment.client_id
        vat.updated_by = request.user
        vat.period_start = assesment.period_end + relativedelta(days=1)
        vat.period_end = assesment.period_end + relativedelta(assesment.period_end + relativedelta(days=1), assesment.period_start)
        vat.HMRC_deadline = vat.period_end + relativedelta(months=1) # type: ignore
        vat.save()
        messages.success(request, f'New Limited VAT Tracker has been created {vat}')

      context['form'] = LimitedVATTrackerChangeForm(instance=assesment)
      messages.success(request, f'Limited VAT Tracker has been updated having id {vat_id}!')
      return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_home_name)
    else:
      messages.error(request, f'Updating Limited VAT Tracker having id {vat_id} failed due to invalid data!')
  return render(request, template_name='companies/update.html', context=context)

@login_required
@allowed_for_superuser(
  message="Sorry! You are not authorized to delete this.",
  redirect_to=URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_home_name)
def delete_limited_vat_tracker(request, vat_id:int):
  context = {
    **URLS,
    'page_title': 'Delete Limited VAT Tracker',
    'id': vat_id,
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_home_name,
    'delete_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_delete_name,
    'form_title': "Limited VAT Tracker Delete Form",
    'form': LimitedVATTrackerDeleteForm()
  }

  try:
    record = LimitedVATTracker.objects.get(vat_id=vat_id)
  except LimitedVATTracker.DoesNotExist:
    messages.error(request, f'Limited VAT Tracker record with id {vat_id}, you are looking for does not exist!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_home_name)
  
  if request.method == 'POST':
    form = LimitedVATTrackerDeleteForm(request.POST)
    context['form'] = form
    if form.is_valid():
      record.delete()
      messages.success(request, f'Limited VAT Tracker has been deleted having id {vat_id}!')
    else:
      messages.error(request, f'Deletion of Limited VAT Tracker having id {vat_id} failed!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_home_name)
  return render(request, template_name='companies/delete.html', context=context)

@login_required
def search_limited_vat_tracker(request, limit: int=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    # get search text from url query parameter
    search_text = request.GET.get('q', '').strip()
    tasks_key = request.GET.get('tasks')

    # if tasks query paramter exists then return tasks
    if tasks_key:
      tasks = {
        'submission_deadline_not_set': get_limited_vats_where_deadline_not_set(),
        'submission_vat_deadline_missed': get_limited_vats_where_deadline_missed(),
        'period_diff_gt_3months': get_limited_vats_where_period_difference_more_than_3months()
      }
      records = tasks.get(tasks_key, [])
      data = serialize(queryset=records, format='json')
      return HttpResponse(data, content_type='application/json')
    
    # filter results using the search_text
    if search_text.strip()=='':
      return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_viewall_name)
    records = db_search_LimitedVATTracker(search_text, limit)
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
def all_limited_vat_tracker(request, limit=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    records = db_all_LimitedVATTracker(limit)
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
@allowed_for_superuser(
  message="Sorry! You are not authorized to export this.",
  redirect_to=URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_VAT_Tracker_home_name)
def export_limited_vat_tracker(request):
  response = HttpResponse(
    content_type='text/csv',
    headers={'Content-Disposition': f'attachment; filename="limited_vat_tracker_{timezone.localtime()}.csv"'},
  )
  # get field names to export these are in '.' separated format for nested fields
  params = request.GET
  field_names = params.get('export_fields', None)
  if field_names:
    field_names = field_names.split(",")
  else:
    field_names = []
  
  default_include_fields = []
  include_fields = field_names if len(field_names)>0 else default_include_fields
  fk_fields = {
    'client_id': LIMITED_FK_FIELDS_FOR_EXPORT
  }
  exclude_fields = ['vat_id']
  keep_include_fields = False
  show_others = (include_fields==default_include_fields)
  export_to_csv(
    django_model = LimitedVATTracker,
    write_to = response,
    include_fields = include_fields,
    exclude_fields = exclude_fields,
    keep_include_fields = keep_include_fields,
    show_others = show_others,
    fk_fields = fk_fields
    )
  return response


# =============================================================================================================
# =============================================================================================================
# LimitedConfirmationStatementTracker
def get_limited_statements_where_deadline_not_set():
  query = Q(client_id__is_active=True) & Q(company_house_deadline = None)
  return LimitedConfirmationStatementTracker.ordered_manager.ordered_filter(query)

def get_limited_statements_where_deadline_missed():
  query = Q(client_id__is_active=True) & Q(company_house_deadline__lt = timezone.now()) & Q(is_submitted=False)
  return LimitedConfirmationStatementTracker.ordered_manager.ordered_filter(query)


@login_required
def home_limited_confirmation_statement_tracker(request):
  pk_field = 'statement_id'
  exclude_fields = []
  keep_include_fields = True
  field_ordering = [
    "statement_id",
    "client_id",
    "reg_num",
    "company_house_deadline",
    "is_submitted",
    "submitted_by",
    "submission_date",
    "is_documents_uploaded",
    "remarks",
    "updated_by",
    "last_updated_on",
  ]
  model_fields = get_field_names_from_model(LimitedConfirmationStatementTracker)
  model_fields.append('reg_num')
  fk_fields = {
      'updated_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'client_id': { 'details_url_without_argument': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_details_url, 'repr-format': HTML_Generator.Limited_client_id_repr_format, 'href-url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_update_url,},
      'reg_num': { 'details_url_without_argument': '/companies/LTD/details/', 'repr-format': r'{company_reg_number}', 'data-field': 'fields.client_id'},
      }
  context = {
    **URLS,
    'caption': 'View Confirmation Statement Tracker',
    'page_title': 'View Confirmation Statement Tracker',
    
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_create_name,
    'export_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_export_name,

    'counts': True,
    'limited_statement_counts': True,
    'statement_deadline_not_set': get_limited_statements_where_deadline_not_set().count(),
    'statement_deadline_missed': get_limited_statements_where_deadline_missed().count(),

    'template_tag': generate_template_tag_for_model(LimitedConfirmationStatementTracker, pk_field=pk_field, show_id=True, exclude_fields=exclude_fields, ordering=field_ordering, fk_fields=fk_fields, keep_include_fields=keep_include_fields),
    'data_container': generate_data_container_table(LimitedConfirmationStatementTracker, pk_field=pk_field, show_id=True, exclude_fields=exclude_fields, ordering=field_ordering, keep_include_fields=keep_include_fields, ),

    'frontend_data':{
      'all_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Confirmation_Statement_Tracker_viewall_url,
      'search_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Confirmation_Statement_Tracker_search_url,
      'update_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Confirmation_Statement_Tracker_update_url,
      'delete_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Confirmation_Statement_Tracker_delete_url,  
      'model_fields': model_fields
    },

    "export_field_names": group_fields_by_uniqueness({
      "LimitedConfirmationStatementTracker": get_field_names_with_label(LimitedConfirmationStatementTracker),
    })
  }
  return render(request=request, template_name='companies/home.html', context=context)

@login_required
def view_limited_confirmation_statement_tracker(request):
  return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_home_name)

@login_required
def create_limited_confirmation_statement_tracker(request):
  context = {
    **URLS,

    'page_title': 'Create Limited Confirmation Statement Tracker',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_home_name,
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_create_name,
    'form_title': 'Limited Confirmation Statement Tracker Creation Form',
    'form': LimitedConfirmationStatementTrackerCreationForm()
  }

  if request.method == 'POST':
    form = LimitedConfirmationStatementTrackerCreationForm(request.POST)
    context['form'] = form
    if form.is_valid():
      assesment = form.save()
      assesment.set_defaults(request)
      assesment.save()
      messages.success(request, f'New Limited Confirmation Statement Tracker has been created with id {assesment.statement_id}!')
      context['form'] = LimitedConfirmationStatementTrackerCreationForm()
    else:
      messages.error(request, f'Action failed due to invalid data!')
  return render(request, template_name='companies/create.html', context=context)

@login_required
def update_limited_confirmation_statement_tracker(request, statement_id:int):
  context = {
    **URLS,
    'page_title': f'Update Limited Confirmation Statement Tracker',
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_home_name,
    'id': statement_id,
    'update_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_update_name,
    'form_title': 'Limited Confirmation Statement Tracker Update Form',
    'form': LimitedConfirmationStatementTrackerChangeForm()
  }

  try:
    record =  LimitedConfirmationStatementTracker.objects.get(statement_id=statement_id)
    if record.is_submitted:
      messages.error(request, message=f"Limited Confirmation Statement Tracker {statement_id} is submitted therefore can't be updated!")
      return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_home_name)
    context['form'] = LimitedConfirmationStatementTrackerChangeForm(instance=record)
  except LimitedConfirmationStatementTracker.DoesNotExist:
    messages.error(request, f'Limited Confirmation Statement Tracker having id {statement_id} does not exists!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_home_name)
    raise Http404

  if request.method == 'POST':
    form = LimitedConfirmationStatementTrackerChangeForm(request.POST, instance=record)
    context['form'] = form
    if form.is_valid():
      assesment = form.save(commit=False)
      assesment.set_defaults(request)
      assesment.save()
      
      # Create Limited Confirmation Statement Tracker
      if assesment.is_submitted:
        statement = LimitedConfirmationStatementTracker()
        statement.client_id = assesment.client_id
        statement.company_house_deadline = assesment.company_house_deadline + relativedelta(years=1) #- relativedelta(days=1)
        statement.set_defaults(request)
        statement.save()
        messages.success(request, f'New Limited Confirmation Statement Tracker has been created {statement}!')

      context['form'] = LimitedConfirmationStatementTrackerChangeForm(instance=assesment)
      messages.success(request, f'Limited Confirmation Statement Tracker has been updated having id {statement_id}!')
      return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_home_name)
    else:
      messages.error(request, f'Updating Limited Confirmation Statement Tracker having id {statement_id} failed due to invalid data!')
  return render(request, template_name='companies/update.html', context=context)

@login_required
@allowed_for_superuser(
  message="Sorry! You are not authorized to delete this.",
  redirect_to=URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_home_name)
def delete_limited_confirmation_statement_tracker(request, statement_id:int):
  context = {
    **URLS,
    'page_title': 'Delete Limited Confirmation Statement Tracker',
    'id': statement_id,
    'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_home_name,
    'delete_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_delete_name,
    'form_title': "Limited Confirmation Statement Tracker Delete Form",
    'form': LimitedConfirmationStatementTrackerDeleteForm()
  }

  try:
    record = LimitedConfirmationStatementTracker.objects.get(statement_id=statement_id)
  except LimitedConfirmationStatementTracker.DoesNotExist:
    messages.error(request, f'Limited Confirmation Statement Tracker record with id {statement_id}, you are looking for does not exist!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_home_name)
  
  if request.method == 'POST':
    form = LimitedConfirmationStatementTrackerDeleteForm(request.POST)
    context['form'] = form
    if form.is_valid():
      record.delete()
      messages.success(request, f'Limited Confirmation Statement Tracker has been deleted having id {statement_id}!')
    else:
      messages.error(request, f'Deletion of Limited Confirmation Statement Tracker having id {statement_id} failed!')
    return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_home_name)
  return render(request, template_name='companies/delete.html', context=context)

@login_required
def search_limited_confirmation_statement_tracker(request, limit: int=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    # get search text from url query parameter
    search_text = request.GET.get('q', '').strip()
    tasks_key = request.GET.get('tasks')

    # if tasks query paramter exists then return tasks
    if tasks_key:
      tasks = {
        'statement_deadline_not_set': get_limited_statements_where_deadline_not_set(),
        'statement_deadline_missed': get_limited_statements_where_deadline_missed(),
      }
      records = tasks.get(tasks_key, [])
      data = serialize(queryset=records, format='json')
      return HttpResponse(data, content_type='application/json')
    
    # filter results using the search_text
    if search_text.strip()=='':
      return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_viewall_name)
    records = db_search_LimitedConfirmationStatementTracker(search_text, limit)
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
def all_limited_confirmation_statement_tracker(request, limit=-1):
  if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
    records = db_all_LimitedConfirmationStatementTracker(limit)
    data = serialize(queryset=records, format='json')
    return HttpResponse(data, content_type='application/json')
  raise Http404

@login_required
@allowed_for_superuser(
  message="Sorry! You are not authorized to export this.",
  redirect_to=URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Confirmation_Statement_Tracker_home_name)
def export_limited_confirmation_statement_tracker(request):
  response = HttpResponse(
    content_type='text/csv',
    headers={'Content-Disposition': f'attachment; filename="limited_confirmation_statement_tracker_{timezone.localtime()}.csv"'},
  )
  # get field names to export these are in '.' separated format for nested fields
  params = request.GET
  field_names = params.get('export_fields', None)
  if field_names:
    field_names = field_names.split(",")
  else:
    field_names = []
  
  default_include_fields = []
  include_fields = field_names if len(field_names)>0 else default_include_fields
  exclude_fields = ['statement_id']
  fk_fields = {
    'client_id': LIMITED_FK_FIELDS_FOR_EXPORT
  }
  keep_include_fields = False
  show_others = (include_fields==default_include_fields)
  export_to_csv(
    django_model = LimitedConfirmationStatementTracker,
    write_to = response,
    include_fields = include_fields,
    exclude_fields = exclude_fields,
    keep_include_fields = keep_include_fields,
    show_others = show_others,
    fk_fields = fk_fields
    )
  return response


###########################################
# Merged trackers view
merged_tracker_home_redirect_page = URL_NAMES_PREFIXED_WITH_APP_NAME.Merged_Tracker_home_name

@login_required
def home_merged_tracker(request):
  pk_field = 'tracker_id'
  exclude_fields = ['is_updated']
  include_fields = ['tracker_id', 'client_id', 'job_description', 'deadline', 'remarks','is_completed', 'has_issue', 'complete_date', 'done_by', 'created_by','creation_date', 'issue_created_by']
  limited_tracker_fk_fields = {
    'created_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
    'issue_created_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
    'done_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
    'submitted_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
    'prepared_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
    'assigned_to': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
    'client_id': { 'details_url_without_argument': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_details_url, 'repr-format': HTML_Generator.Limited_client_id_repr_format, 'href-url':Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_update_url },
    'incomplete_tasks': { 'details_url_without_argument': '/companies/LTrc/search/?client_id=', 'repr-format': r'{length}'}
    }
  selfassesment_tracker_fk_fields = {
    'created_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
    'issue_created_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
    'done_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
    'submitted_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
    'prepared_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
    'assigned_to': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
    'client_id': { 'details_url_without_argument': Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_details_url, 'repr-format': HTML_Generator.Selfassesment_client_id_repr_format, 'href-url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_update_url },
    'incomplete_tasks': { 'details_url_without_argument': '/companies/SATrc/search/?client_id=', 'repr-format': r'{length}'}
    }
  
  keep_include_fields = True
  context = {
    **URLS,
    'page_title': 'View Tracker',
    'caption': 'View Tracker',

    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Merged_Tracker_create_name,
    'export_name': URL_NAMES_PREFIXED_WITH_APP_NAME.Merged_Tracker_export_name,

    'create_limited_tracker': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_Tracker_create_name,
    'create_selfassesment_tracker': URL_NAMES_PREFIXED_WITH_APP_NAME.Selfassesment_Tracker_create_name,

    'counts': True,
    'tracker_task_counts': True,
    'new_customers': get_limited_trackers_where_tasks_customers_are_new().count() + get_selfassesment_trackers_where_tasks_customers_are_new().count(),
    'future_incomplete_tasks': get_limited_trackers_where_future_tasks_are_incomplete().count() + get_selfassesment_trackers_where_future_tasks_are_incomplete().count(),
    'todays_incomplete_tasks': get_limited_trackers_where_todays_tasks_are_incomplete().count() + get_selfassesment_trackers_where_todays_tasks_are_incomplete().count(),
    'previous_incomplete_tasks': get_limited_trackers_where_previous_tasks_are_incomplete().count() + get_selfassesment_trackers_where_previous_tasks_are_incomplete().count(),
    'task_has_issue': get_limited_trackers_where_tasks_has_issues().count() + get_selfassesment_trackers_where_tasks_has_issues().count(),
    'my_tasks': get_limited_trackers_where_tasks_assigned_to_user(request.user).count() + get_selfassesment_trackers_where_tasks_assigned_to_user(request.user).count(),

    'data_container': generate_data_container_table(LimitedTracker, pk_field=pk_field, show_id=True, include_fields=include_fields, exclude_fields=exclude_fields, keep_include_fields=keep_include_fields),
    'selfassesment_tracker_template': generate_template_tag_for_model(SelfassesmentTracker, pk_field=pk_field, show_id=True, include_fields=include_fields, exclude_fields=exclude_fields, keep_include_fields=keep_include_fields, fk_fields=selfassesment_tracker_fk_fields, tag_id="selfassesment_tracker_template"),
    'limited_tracker_template': generate_template_tag_for_model(LimitedTracker, pk_field=pk_field, show_id=True, include_fields=include_fields, exclude_fields=exclude_fields, keep_include_fields=keep_include_fields, fk_fields=limited_tracker_fk_fields, tag_id="limited_tracker_template"),

    'frontend_data': {
      "Limited": {
        'create_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Tracker_create_url,
        'viewall_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Tracker_viewall_url,
        'search_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Tracker_search_url,
        'update_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Tracker_update_url,
        'delete_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Tracker_delete_url,
        "model_fields": get_field_names_from_model(SelfassesmentTracker),
      },
      "Selfassesment": {
        'create_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Tracker_create_url,
        'viewall_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Tracker_viewall_url,
        'search_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Tracker_search_url,
        'update_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Tracker_update_url,
        'delete_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Tracker_delete_url,
        "model_fields": get_field_names_from_model(LimitedTracker),
      },
    },
    "export_field_names": group_fields_by_uniqueness({
      "LimitedTracker": get_field_names_with_label(LimitedTracker),
      "SelfassesmentTracker": get_field_names_with_label(SelfassesmentTracker),
    })
  }
  return render(request, 'companies/merged_tracker.html', context=context)

@login_required
def create_merged_tracker(request):
  context = {
    **URLS,
    'page_title': 'Create Tracker',
    
    'view_url': merged_tracker_home_redirect_page,
    'create_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Merged_Tracker_create_name,

    'form_title': 'Tracker Creation Form',
    'form': MergedTrackerCreateionForm(),

    'redirect_to': URL_NAMES_PREFIXED_WITH_APP_NAME.Merged_Tracker_create_name,

    'frontend_data':{
      "Limited": {
        'create_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_Tracker_create_url,
        'viewall_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_viewall_url,
        'search_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_search_url,
        'repr_format': FK_Formats.Limited_client_id_repr_format,
        'redirect_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Merged_Tracker_create_name
      },
      "Selfassesment": {
        'create_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Tracker_create_url,
        'viewall_url': Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_viewall_url,
        'search_url':  Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_search_url,
        'repr_format': FK_Formats.Selfassesment_client_id_repr_format,
        'redirect_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Merged_Tracker_create_name
      },
    }
  }
  return render(request, template_name='companies/merged_tracker_create.html', context=context)

@login_required
def export_merged_tracker(request:HttpRequest):
  response = HttpResponse(
    content_type='text/csv; charset=utf-8',
    headers={'Content-Disposition': f'attachment; filename="merged_tracker_{timezone.localtime()}.csv"'},
  )
  # get field names to export these are in '.' separated format for nested fields
  params = request.GET
  field_names = params.get('export_fields', None)
  if field_names:
    field_names = field_names.split(",")
  else:
    field_names = []
  
  default_include_fields = []
  include_fields = field_names if len(field_names)>0 else default_include_fields
  exclude_fields = set(['is_updated'])
  keep_include_fields = True
  show_others = (include_fields==default_include_fields)
  export_to_csv(
    django_model = LimitedTracker,
    write_to = response,
    include_fields = include_fields,
    exclude_fields = exclude_fields,
    keep_include_fields = keep_include_fields,
    show_others = show_others
    )
  export_to_csv(
    django_model = SelfassesmentTracker,
    write_to = response,
    include_fields = include_fields,
    exclude_fields = exclude_fields,
    keep_include_fields = keep_include_fields,
    show_others = show_others,
    write_header_row=False
    )
  return response
