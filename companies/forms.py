from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from itertools import chain
from django.utils.translation import gettext_lazy as _
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .fields import SearchableModelField, Select, Fieldset
from .url_variables import Full_URL_PATHS_WITHOUT_ARGUMENTS

from .models import Selfassesment, SelfassesmentAccountSubmission, SelfassesmentTracker, SelfassesmentAccountSubmissionTaxYear, SelfemploymentIncomeAndExpensesDataCollection
from .models import Limited, LimitedTracker, LimitedSubmissionDeadlineTracker, LimitedVATTracker, LimitedConfirmationStatementTracker, LimitedOnboardingTasks

# from .queries import db_all_Limited, db_all_LimitedConfirmationStatementTracker, db_all_LimitedSubmissionDeadlineTracker, \
#     db_all_LimitedTracker, db_all_LimitedVATTracker
# from .queries import db_all_Selfassesment, db_all_SelfassesmentAccountSubmission, db_all_SelfassesmentAccountSubmissionTaxYear, \
#     db_all_SelfassesmentTracker

from .repr_formats import Forms

from django.conf import settings

# dummy import
# uncomment next line before migrating
if settings.WANT_TO_MIGRATE:
    from .dummy_class import *


from users.models import CustomUser
search_users_url_path = '/u/search/'
all_users_url_path = '/u/all/'


def get_date_today(date_format = '%Y-%m-%d'):
    today = timezone.datetime.strftime(timezone.now(), date_format)
    return today

class SelfassesmentCreationForm(forms.ModelForm):
    start_date = forms.DateField(
        label='Start Date',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'placehoder': 'Selfassesment Start Date'})
    )
    date_of_registration = forms.DateField(
        label='Registration date',
        widget=forms.DateInput(attrs={'type': 'date', 'value': get_date_today, 'placehoder': 'Registration date'})
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date',})
    )
    driving_license_expiry_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date',})
    )
    passport_expiry_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date',})
    )

    class Meta:
        model = Selfassesment
        fields = (
            # 'client_id',
            # 'created_by',
            # 'is_updated',
            'client_rating',
            'selfassesment_type',
            'date_of_registration',
            'is_active',
            'remarks',

            'client_file_number',
            'client_name',
            'start_date',

            'date_of_birth',
            'PAYE_number',
            'personal_phone_number',
            'personal_email',
            'personal_address',
            'personal_post_code',
            'driving_license_expiry_date',
            'passport_expiry_date',

            'AOR_number',
            'business_phone_number',
            'business_email',
            'business_address',
            'business_post_code',

            'HMRC_agent',
            'HMRC_referance',
            'UTR',
            'NINO',
            'gateway_id',
            'gateway_password',
            
            'bank_name',
            'bank_account_number',
            'bank_sort_code',
            'bank_account_holder_name',
            )
        fieldsets = (
            Fieldset(
                title = 'Client Info',
                fields = ('client_rating', 'client_file_number', 'selfassesment_type', 'date_of_registration', 'client_name', 'remarks', 'is_active', 'start_date')
                ),
            Fieldset(
                title = 'Personal Info',
                fields = ('date_of_birth', 'personal_phone_number', 'personal_email', 'personal_address', 'personal_post_code', 'driving_license_expiry_date', 'passport_expiry_date', )
                ),
            Fieldset(
                title = 'HMRC Details',
                fields =  ('HMRC_referance', 'UTR', 'NINO', 'HMRC_agent', 'gateway_id', 'gateway_password', )
            ),
            Fieldset(
                title = 'Business Info', 
                fields = ('business_phone_number', 'business_email', 'business_address', 'business_post_code', 'PAYE_number', 'AOR_number', )
                ),
            Fieldset(
                title = 'Bank Info',
                fields = ('bank_name', 'bank_account_number', 'bank_sort_code', 'bank_account_holder_name',)
                ),
        )

        def clean_client_file_number(self):
            return self.cleaned_data["client_file_number"].upper()


class SelfassesmentChangeForm(forms.ModelForm):
    start_date = forms.DateField(
        label='Start Date',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'placehoder': 'Selfassesment Start Date'})
    )
    date_of_registration = forms.DateField(
        label='Registration date',
        widget=forms.DateInput(attrs={'type': 'date', 'value': get_date_today, 'placehoder': 'Registration date'})
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date',})
    )
    driving_license_expiry_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date',})
    )
    passport_expiry_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date',})
    )
    
    class Meta:
        model = Selfassesment
        fields = (
            # 'client_id',
            # 'created_by',
            # 'is_updated',
            'client_rating',
            'selfassesment_type',
            'date_of_registration',
            'is_active',
            'remarks',

            'client_file_number',
            'client_name',
            'start_date',

            'date_of_birth',
            'PAYE_number',
            'personal_phone_number',
            'personal_email',
            'personal_address',
            'personal_post_code',
            'driving_license_expiry_date',
            'passport_expiry_date',

            'AOR_number',
            'business_phone_number',
            'business_email',
            'business_address',
            'business_post_code',

            'HMRC_agent',
            'HMRC_referance',
            'UTR',
            'NINO',
            'gateway_id',
            'gateway_password',
            
            'bank_name',
            'bank_account_number',
            'bank_sort_code',
            'bank_account_holder_name',
            )
        fieldsets = (
            Fieldset(
                title = 'Client Info',
                fields = ('client_rating', 'client_file_number', 'selfassesment_type', 'date_of_registration', 'client_name', 'remarks', 'is_active', 'start_date')
                ),
            Fieldset(
                title = 'Personal Info',
                fields = ('date_of_birth', 'personal_phone_number', 'personal_email', 'personal_address', 'personal_post_code', 'driving_license_expiry_date', 'passport_expiry_date',)
                ),
            Fieldset(
                title = 'HMRC Details',
                fields =  ('HMRC_referance', 'UTR', 'NINO', 'HMRC_agent', 'gateway_id', 'gateway_password', )
            ),
            Fieldset(
                title = 'Business Info', 
                fields = ('business_phone_number', 'business_email', 'business_address', 'business_post_code', 'PAYE_number', 'AOR_number', )
                ),
            Fieldset(
                title = 'Bank Info',
                fields = ('bank_name', 'bank_account_number', 'bank_sort_code', 'bank_account_holder_name',)
                ),
        )
        
    def clean_client_file_number(self):
        return self.cleaned_data["client_file_number"].upper()

class SelfassesmentDeleteForm(forms.ModelForm):
    agree = forms.BooleanField(label='I want to proceed.', required=True)
    class Meta:
        model = Selfassesment
        fields = ()


class SelfemploymentIncomeAndExpensesDataCollectionAuthFormForClients(forms.Form):
    utr = forms.CharField(label="Enter your UTR", max_length=10, required=True)

    class Meta:
        fields = ('utr',)

class SelfemploymentIncomeAndExpensesDataCollectionCreationFormForClients(forms.ModelForm):
    selfassesment = SearchableModelField(
        queryset=Selfassesment.objects.all(),
        label = 'Client Name',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_viewall_url,
        repr_format = Forms.Selfassesment_client_id_repr_format,
        model=Selfassesment,
        choices=Selfassesment.objects.all().only('client_id', 'client_name'),
        fk_field='client_id',
        empty_label=None,
        disabled=True,
        required=False,
        render_options=False
        )
    tax_year = SearchableModelField(
        queryset=SelfassesmentAccountSubmissionTaxYear.objects.all(),
        label = 'Tax Year',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Account_Submission_Tax_Year_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Account_Submission_Tax_Year_viewall_url,
        repr_format = Forms.Selfassemsent_tax_year_repr_format,
        model=SelfassesmentAccountSubmissionTaxYear,
        choices=SelfassesmentAccountSubmissionTaxYear.objects.all(),
        fk_field='id',
        empty_label=None,
        disabled=True,
        required=False,
        render_options=False
    )

    class Meta:
        model = SelfemploymentIncomeAndExpensesDataCollection
        fields = (
            "selfassesment",
            "tax_year",

            # incomes
            "uber_income",
            "bolt_income",
            "free_now_income",
            "other_income",
            "total_grant_income",
            "employment_income",
            "income_note",

            # expenses
            "telephone_expense",
            "congestion_expense",
            "insurance_expense",
            "MOT_expense",
            "licence_expense",
            "repair_expense",
            "road_tax_expense",
            "breakdown_expense",
            "car_value_expense",

            'is_submitted'
            )
        fieldsets = (
            Fieldset(
                title = 'Info',
                fields = (
                    'selfassesment',
                    'tax_year'
                    )
                ),
            Fieldset(
                title = 'Total income for the year',
                fieldset_message = 'Please make sure you sent the proof of income(Bank statements/other documents) to our Email(info@rivia-solutions.com) or WhatsApp.',
                fields = (
                    "uber_income",
                    "bolt_income",
                    "free_now_income",
                    "other_income",
                    "total_grant_income",
                    "employment_income",
                    "income_note",
                    )
                ),
            Fieldset(
                title = 'Expenses',
                fields = (
                    "telephone_expense",
                    "congestion_expense",
                    "insurance_expense",
                    "MOT_expense",
                    "licence_expense",
                    "repair_expense",
                    "road_tax_expense",
                    "breakdown_expense",
                    "car_value_expense",
                    )
                ),
            Fieldset(
                title='Agreement',
                fieldset_message='I hereby declare that the information provided is true and correct.',
                fields=['is_submitted']
            )
        )
        message_for_fields={
            'is_submitted': 'After submitting with Ready to Submit marked you can not edit but only view. If you need to update data after submitting with "Ready to Submit" marked please contact us.'
        }

class SelfemploymentIncomeAndExpensesDataCollectionCreationForm(forms.ModelForm):
    selfassesment = SearchableModelField(
        queryset=Selfassesment.objects.all(),
        label = 'Client Name',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_viewall_url,
        repr_format = Forms.Selfassesment_client_id_repr_format,
        model=Selfassesment,
        choices=Selfassesment.objects.all().only('client_id', 'client_name'),
        fk_field='client_id',
        empty_label=None
        )
    tax_year = SearchableModelField(
        queryset=SelfassesmentAccountSubmissionTaxYear.objects.all(),
        label = 'Tax Year',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Account_Submission_Tax_Year_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Account_Submission_Tax_Year_viewall_url,
        repr_format = Forms.Selfassemsent_tax_year_repr_format,
        model=SelfassesmentAccountSubmissionTaxYear,
        choices=SelfassesmentAccountSubmissionTaxYear.objects.all(),
        fk_field='id',
        empty_label=None,
    )

    class Meta:
        model = SelfemploymentIncomeAndExpensesDataCollection
        fields = (
            "selfassesment",
            "tax_year",

            # incomes
            "uber_income",
            "bolt_income",
            "free_now_income",
            "other_income",
            "total_grant_income",
            "employment_income",
            "income_note",

            # expenses
            "telephone_expense",
            "congestion_expense",
            "insurance_expense",
            "MOT_expense",
            "licence_expense",
            "repair_expense",
            "road_tax_expense",
            "breakdown_expense",
            "car_value_expense",

            'is_submitted'
            )
        fieldsets = (
            Fieldset(
                title = 'Info',
                fields = (
                    'selfassesment',
                    'tax_year'
                    )
                ),
            Fieldset(
                title = 'Incomes',
                fields = (
                    "uber_income",
                    "bolt_income",
                    "free_now_income",
                    "other_income",
                    "total_grant_income",
                    "employment_income",
                    "income_note",
                    )
                ),
            Fieldset(
                title = 'Expenses',
                fields = (
                    "telephone_expense",
                    "congestion_expense",
                    "insurance_expense",
                    "MOT_expense",
                    "licence_expense",
                    "repair_expense",
                    "road_tax_expense",
                    "breakdown_expense",
                    "car_value_expense",
                    )
                ),
            Fieldset(
                title = 'Agreement',
                fields = (
                    'is_submitted',
                    )
                ),
        )

class SelfemploymentIncomeAndExpensesDataCollectionUpdateForm(forms.ModelForm):
    selfassesment = SearchableModelField(
        queryset=Selfassesment.objects.all(),
        label = 'Client Name',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_viewall_url,
        repr_format = Forms.Selfassesment_client_id_repr_format,
        model=Selfassesment,
        choices=Selfassesment.objects.all().only('client_id', 'client_name'),
        fk_field='client_id',
        empty_label=None,
        )
    tax_year = SearchableModelField(
        queryset=SelfassesmentAccountSubmissionTaxYear.objects.all(),
        label = 'Tax Year',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Account_Submission_Tax_Year_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Account_Submission_Tax_Year_viewall_url,
        repr_format = Forms.Selfassemsent_tax_year_repr_format,
        model=SelfassesmentAccountSubmissionTaxYear,
        choices=SelfassesmentAccountSubmissionTaxYear.objects.all(),
        fk_field='id',
        empty_label=None,
    )

    class Meta:
        model = SelfemploymentIncomeAndExpensesDataCollection
        fields = (
            "selfassesment",
            "tax_year",

            # incomes
            "uber_income",
            "bolt_income",
            "free_now_income",
            "other_income",
            "total_grant_income",
            "employment_income",
            "income_note",

            # expenses
            "telephone_expense",
            "congestion_expense",
            "insurance_expense",
            "MOT_expense",
            "licence_expense",
            "repair_expense",
            "road_tax_expense",
            "breakdown_expense",
            "car_value_expense",

            'is_submitted'
            )
        fieldsets = (
            Fieldset(
                title = 'Info',
                fields = (
                    'selfassesment',
                    'tax_year'
                    )
                ),
            Fieldset(
                title = 'Incomes',
                fields = (
                    "uber_income",
                    "bolt_income",
                    "free_now_income",
                    "other_income",
                    "total_grant_income",
                    "employment_income",
                    "income_note",
                    )
                ),
            Fieldset(
                title = 'Expenses',
                fields = (
                    "telephone_expense",
                    "congestion_expense",
                    "insurance_expense",
                    "MOT_expense",
                    "licence_expense",
                    "repair_expense",
                    "road_tax_expense",
                    "breakdown_expense",
                    "car_value_expense",
                    )
                ),
            Fieldset(
                title = 'Agreement',
                fields = (
                    'is_submitted',
                    )
                ),
        )

class SelfemploymentIncomeAndExpensesDataCollectionDeleteForm(forms.ModelForm):
    agree = forms.BooleanField(label='I want to proceed.', required=True)
    class Meta:
        model = SelfemploymentIncomeAndExpensesDataCollection
        fields = ()


class SelfassesmentAccountSubmissionCreationForm(forms.ModelForm):
    assigned_to = SearchableModelField(
        queryset=CustomUser.objects.all(),
        search_url = search_users_url_path,
        all_url = all_users_url_path,
        repr_format = Forms.CustomUser_repr_format,
        model = CustomUser,
        choices = CustomUser.objects.all().only('user_id', 'first_name'),
        fk_field = 'user_id',
        disabled = False,
        required = False,
        empty_label = None # remove default option '------' from select menu
        )
    client_id = SearchableModelField(
        queryset=Selfassesment.objects.all(),
        label = 'Client Name',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_viewall_url,
        repr_format = Forms.Selfassesment_client_id_repr_format,
        model=Selfassesment,
        choices=Selfassesment.objects.all().only('client_id', 'client_name'),
        fk_field='client_id',
        empty_label=None
        )
    tax_year = SearchableModelField(
        queryset=SelfassesmentAccountSubmissionTaxYear.objects.all(),
        label = 'Tax Year',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Account_Submission_Tax_Year_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Account_Submission_Tax_Year_viewall_url,
        repr_format = Forms.Selfassemsent_tax_year_repr_format,
        model=SelfassesmentAccountSubmissionTaxYear,
        choices=SelfassesmentAccountSubmissionTaxYear.objects.all(),
        fk_field='id',
        empty_label=None
    )
    appointment_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date',}), required=False)
    request_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', "value": get_date_today()}), required=False)

    class Meta:
        model = SelfassesmentAccountSubmission
        fields = (
            # "submission_id",
            'assigned_to',
            "client_id",
            "status",
            "appointment_date",
            "tax_year",
            "request_date",
            "remarks",
            "payment_status",
            "payment_method",
            "paid_amount",
            # "prepared_by",
            # "submitted_by",
            # "is_submitted",
            # "last_updated_by",
            # "last_updated_on",
            )
        labels = {
            'client_id': _('Client Name'),
        }
        message_for_fields = {}

    def clean_appointment_date(self):
        status = self.cleaned_data.get('status')
        appointment_date = self.cleaned_data.get('appointment_date')
        if status=="BOOK APPOINTMENT" and not appointment_date:
            raise ValidationError("Status is BOOK APPOINTMENT. Therefore, Appointment Date is required.")
        return appointment_date
    
    def clean_request_date(self):
        client_id = self.cleaned_data.get("client_id")
        tax_year = self.cleaned_data.get("tax_year")
        request_date = self.Meta.model.get_request_date(client_id, tax_year)
        form_request_date = self.cleaned_data.get("request_date")
        
        if request_date: return request_date
        if form_request_date: return form_request_date
        raise ValidationError(f"Request Date is required because there isn't any previous records with Client ID: {client_id} and Tax Year: {tax_year}")


class SelfassesmentAccountSubmissionChangeForm(forms.ModelForm):
    assigned_to = SearchableModelField(
        queryset=CustomUser.objects.all(),
        search_url = search_users_url_path,
        all_url = all_users_url_path,
        repr_format = Forms.CustomUser_repr_format,
        model = CustomUser,
        choices = CustomUser.objects.all().only('user_id', 'first_name'),
        fk_field = 'user_id',
        disabled = False,
        required = False,
        empty_label = None # remove default option '------' from select menu
        )
    client_id = SearchableModelField(
        queryset=Selfassesment.objects.all(),
        label = 'Client Name',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_viewall_url,
        repr_format = Forms.Selfassesment_client_id_repr_format,
        model=Selfassesment,
        choices=Selfassesment.objects.all().only('client_id', 'client_name'),
        fk_field='client_id',
        empty_label=None,
        disabled=False
        )
    submitted_by = SearchableModelField(
        queryset=CustomUser.objects.all(),
        search_url = search_users_url_path,
        all_url = all_users_url_path,
        repr_format = Forms.CustomUser_repr_format,
        model=CustomUser,
        choices=CustomUser.objects.all().only('user_id', 'first_name'),
        fk_field='user_id',
        empty_label=None,
        disabled=False,
        required = False
        )
    prepared_by = SearchableModelField(
        queryset=CustomUser.objects.all(),
        search_url = search_users_url_path,
        all_url = all_users_url_path,
        repr_format = Forms.CustomUser_repr_format,
        model=CustomUser,
        choices=CustomUser.objects.all().only('user_id', 'first_name'),
        fk_field='user_id',
        empty_label=None,
        disabled=False,
        required = False
        )
    tax_year = SearchableModelField(
        queryset=SelfassesmentAccountSubmissionTaxYear.objects.all(),
        label = 'Tax Year',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Account_Submission_Tax_Year_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Account_Submission_Tax_Year_viewall_url,
        repr_format = Forms.Selfassemsent_tax_year_repr_format,
        model=SelfassesmentAccountSubmissionTaxYear,
        choices=SelfassesmentAccountSubmissionTaxYear.objects.all(),
        fk_field='id',
        empty_label=None
    )
    appointment_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    # request_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = SelfassesmentAccountSubmission
        fields = (
            # "submission_id",
            'assigned_to',
            "client_id",
            "status",
            "appointment_date",
            # "request_date",
            "tax_year",
            "remarks",
            "payment_status",
            "payment_method",
            "paid_amount",
            "prepared_by",
            "submitted_by",
            # "is_submitted",
            # "last_updated_by",
            # "last_updated_on",
            # 'is_updated',
            )
        labels = {
            'client_id': _('Client Name'),
        }
    def clean_appointment_date(self):
        status = self.cleaned_data.get('status')
        appointment_date = self.cleaned_data.get('appointment_date')
        if status=="BOOK APPOINTMENT" and not appointment_date:
            raise ValidationError("Status is BOOK APPOINTMENT. Therefore, Appointment Date is required.")
        return appointment_date



class SelfassesmentAccountSubmissionDeleteForm(forms.ModelForm):
    agree = forms.BooleanField(label='I want to proceed.', required=True)
    class Meta:
        model = SelfassesmentAccountSubmission
        fields = ()


class Add_All_Selfassesment_to_SelfassesmentAccountSubmission_Form(forms.ModelForm):
    date_of_submission = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'value': get_date_today}))
    submitted_by = SearchableModelField(
        queryset=CustomUser.objects.all(),
        search_url = search_users_url_path,
        all_url = all_users_url_path,
        repr_format = Forms.CustomUser_repr_format,
        model=CustomUser,
        choices=CustomUser.objects.all().only('user_id', 'first_name'),
        fk_field='user_id',
        empty_label=None
        )
    prepared_by = SearchableModelField(
        queryset=CustomUser.objects.all(),
        search_url = search_users_url_path,
        all_url = all_users_url_path,
        repr_format = Forms.CustomUser_repr_format,
        model=CustomUser,
        choices=CustomUser.objects.all().only('user_id', 'first_name'),
        fk_field='user_id',
        empty_label=None,
        )
    
    class Meta:
        model = SelfassesmentAccountSubmission
        fields = (
            # 'submission_id',
            'tax_year', 
            'submitted_by', 
            'prepared_by', 
            'date_of_submission')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tax_year'].required = True


class SelfassesmentTrackerCreationForm(forms.ModelForm):
    deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'value': get_date_today, 'min': get_date_today}))
    client_id = SearchableModelField(
        queryset=Selfassesment.objects.all(),
        label = 'Client Name',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_viewall_url,
        repr_format = Forms.Selfassesment_client_id_repr_format,
        model=Selfassesment,
        choices=Selfassesment.objects.all().only('client_id', 'client_name'),
        fk_field='client_id',
        empty_label=None
        )
    assigned_to = SearchableModelField(
        queryset=CustomUser.objects.all(),
        search_url = search_users_url_path,
        all_url = all_users_url_path,
        repr_format = Forms.CustomUser_repr_format,
        model = CustomUser,
        choices = CustomUser.objects.all().only('user_id', 'first_name'),
        fk_field = 'user_id',
        disabled = False,
        required = False,
        empty_label = None # remove default option '------' from select menu
        )
    
    class Meta:
        model = SelfassesmentTracker
        fields = (
            # 'tracker_id',
            # 'created_by', #request.user
            # 'done_by', #request.user
            'assigned_to',
            'client_id',
            'job_description',
            'remarks',
            'has_issue',
            'deadline', #default timezone now
            # 'complete_date', #default timezone now
            # 'is_completed',
            )

    def clean_deadline(self):
        input_date = self.cleaned_data['deadline']
        current_date = timezone.now().date()
        if not input_date>=current_date:
            raise ValidationError("Deadline can't be a previous date.")
        return input_date

    def clean_remarks(self):
        remarks = self.cleaned_data.get('remarks').strip()
        issue = self.data.get('has_issue')
        if issue and not remarks:
            raise ValidationError("Tracker has issue therefore remarks is required")
        return remarks

class SelfassesmentTrackerChangeForm(forms.ModelForm):
    # complete_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    client_id = SearchableModelField(
        queryset=Selfassesment.objects.all(),
        label = 'Client Name',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_viewall_url,
        repr_format = Forms.Selfassesment_client_id_repr_format,
        model=Selfassesment,
        choices=Selfassesment.objects.all().only('client_id', 'client_name'),
        fk_field='client_id',
        empty_label=None,
        disabled=True
        )
    assigned_to = SearchableModelField(
        queryset=CustomUser.objects.all(),
        search_url = search_users_url_path,
        all_url = all_users_url_path,
        repr_format = Forms.CustomUser_repr_format,
        model = CustomUser,
        choices = CustomUser.objects.all().only('user_id', 'first_name'),
        fk_field = 'user_id',
        disabled = False,
        required = False,
        empty_label = None # remove default option '------' from select menu
        )
    # done_by = SearchableModelField(
    #     queryset=CustomUser.objects.all(),
    #     search_url = search_users_url_path,
    #     all_url = all_users_url_path,
    #     repr_format = Forms.CustomUser_repr_format,
    #     model = CustomUser,
    #     choices = CustomUser.objects.all().only('user_id', 'first_name'),
    #     fk_field = 'user_id',
    #     disabled = True,
    #     required = False,
    #     empty_label = None # remove default option '------' from select menu
    #     )
    
    class Meta:
        model = SelfassesmentTracker
        fields = (
            # 'tracker_id',
            # 'created_by',
            # 'done_by',
            'assigned_to',
            'client_id',
            'job_description',
            'remarks',
            'has_issue',
            # 'complete_date',
            'is_completed',)
    
    def clean_remarks(self):
        remarks = self.cleaned_data.get('remarks').strip()
        issue = self.data.get('has_issue')
        if issue and not remarks:
            raise ValidationError("Tracker has issue therefore remarks is required")
        return remarks

class SelfassesmentTrackerDeleteForm(forms.ModelForm):
    agree = forms.BooleanField(label='I want to proceed.', required=True)
    class Meta:
        model = Selfassesment
        fields = ()


##################################################################################################
class LimitedCreationForm(forms.ModelForm):
    date_of_registration = forms.DateField(
        label='Registration date',
        widget=forms.DateInput(attrs={'type': 'date', 'value': get_date_today, 'placehoder': 'Registration date'})
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date',})
    )

    class Meta:
        model = Limited
        fields = (
            # 'client_id',
            # 'created_by',
            # 'is_updated',
            'client_rating',
            'date_of_registration',
            'is_active',
            'is_payroll',
            'remarks',

            'client_file_number',
            'client_name',
            'company_reg_number',
            'company_auth_code',
            'payment_method',

            'date_of_birth',
            'PAYE_number',
            'director_name',
            'director_phone_number',
            'director_email',
            'director_address',
            'director_post_code',

            'AOR_number',
            'business_phone_number',
            'business_email',
            'business_address',
            'business_post_code',

            'HMRC_agent',
            'HMRC_referance',
            'UTR',
            'NINO',
            'gateway_id',
            'gateway_password',
            
            'bank_name',
            'bank_account_number',
            'bank_sort_code',
            'bank_account_holder_name',

            'vat',
            )
        fieldsets = (
            Fieldset(
                title = 'Client Info',
                fields = ('client_rating', 'client_file_number', 'date_of_registration', 'client_name', 'company_reg_number', 'company_auth_code', 'remarks', 'is_active', 'is_payroll', 'payment_method', )
                ),
            Fieldset(
                title = 'Director Info',
                fields = ('date_of_birth', 'director_name', 'director_phone_number', 'director_email', 'director_address', 'director_post_code', )
                ),
            Fieldset(
                title = 'HMRC Details',
                fields =  ('HMRC_referance', 'UTR', 'NINO', 'HMRC_agent', 'gateway_id', 'gateway_password', )
            ),
            Fieldset(
                title = 'Business Info', 
                fields = ('business_phone_number', 'business_email', 'business_address', 'business_post_code', 'PAYE_number', 'AOR_number', )
                ),
            Fieldset(
                title = 'Bank Info',
                fields = ('bank_name', 'bank_account_number', 'bank_sort_code', 'bank_account_holder_name', 'vat',)
                ),
        )
    def clean_client_file_number(self):
        return self.cleaned_data["client_file_number"].upper()


class LimitedChangeForm(forms.ModelForm):
    date_of_registration = forms.DateField(
        label='Registration date',
        widget=forms.DateInput(attrs={'type': 'date', 'value': get_date_today, 'placehoder': 'Registration date'})
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date',})
    )
    
    class Meta:
        model = Limited
        fields = (
            # 'client_id',
            # 'created_by',
            # 'is_updated',
            'client_rating',
            'date_of_registration',
            'is_active',
            'is_payroll',
            'remarks',

            'client_file_number',
            'client_name',
            'company_reg_number',
            'company_auth_code',
            'payment_method',

            'date_of_birth',
            'PAYE_number',
            'director_name',
            'director_phone_number',
            'director_email',
            'director_address',
            'director_post_code',

            'AOR_number',
            'business_phone_number',
            'business_email',
            'business_address',
            'business_post_code',

            'HMRC_agent',
            'HMRC_referance',
            'UTR',
            'NINO',
            'gateway_id',
            'gateway_password',
            
            'bank_name',
            'bank_account_number',
            'bank_sort_code',
            'bank_account_holder_name',

            'vat',
            )
        fieldsets = (
            Fieldset(
                title = 'Client Info',
                fields = ('client_rating', 'client_file_number', 'date_of_registration', 'client_name', 'company_reg_number', 'company_auth_code', 'remarks', 'is_active', 'is_payroll', 'payment_method', )
                ),
            Fieldset(
                title = 'Director Info',
                fields = ('date_of_birth', 'director_name', 'director_phone_number', 'director_email', 'director_address', 'director_post_code', )
                ),
            Fieldset(
                title = 'HMRC Details',
                fields =  ('HMRC_referance', 'UTR', 'NINO', 'HMRC_agent', 'gateway_id', 'gateway_password', )
            ),
            Fieldset(
                title = 'Business Info', 
                fields = ('business_phone_number', 'business_email', 'business_address', 'business_post_code', 'PAYE_number', 'AOR_number', )
                ),
            Fieldset(
                title = 'Bank Info',
                fields = ('bank_name', 'bank_account_number', 'bank_sort_code', 'bank_account_holder_name', 'vat',)
                ),
        )
    def clean_client_file_number(self):
        return self.cleaned_data["client_file_number"].upper()

class LimitedDeleteForm(forms.ModelForm):
    agree = forms.BooleanField(label='I want to proceed.', required=True)
    class Meta:
        model = Limited
        fields = ()


# Limited Onboarding Tasks
class LimitedOnboardingForm(forms.ModelForm):
    class Meta:
        model = LimitedOnboardingTasks
        fields = (
            'client_id',
            'task_id',
            'task_status',
            'note'
        )


# Limited Tracker
class LimitedTrackerCreationForm(forms.ModelForm):
    deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'value': get_date_today, 'min': get_date_today}))
    client_id = SearchableModelField(
        queryset=Limited.objects.all(),
        label = 'Business Name',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_viewall_url,
        repr_format = Forms.Limited_client_id_repr_format,
        model=Limited,
        choices=Limited.objects.all().only('client_id', 'client_name'),
        fk_field='client_id',
        empty_label=None
        )
    assigned_to = SearchableModelField(
        queryset=CustomUser.objects.all(),
        search_url = search_users_url_path,
        all_url = all_users_url_path,
        repr_format = Forms.CustomUser_repr_format,
        model = CustomUser,
        choices = CustomUser.objects.all().only('user_id', 'first_name'),
        fk_field = 'user_id',
        disabled = False,
        required = False,
        empty_label = None # remove default option '------' from select menu
        )
    
    class Meta:
        model = LimitedTracker
        fields = (
            # 'tracker_id',
            # 'created_by', #request.user
            # 'done_by', #request.user
            'assigned_to',
            'client_id',
            'job_description',
            'remarks',
            'has_issue',
            'deadline', #default timezone now
            # 'complete_date', #default timezone now
            # 'is_completed',
            )

    def clean_deadline(self):
        input_date = self.cleaned_data['deadline']
        current_date = timezone.now().date()
        if not input_date>=current_date:
            raise ValidationError("Deadline can't be a previous date.")
        return input_date

    def clean_remarks(self):
        remarks = self.cleaned_data.get('remarks').strip()
        issue = self.data.get('has_issue')
        if issue and not remarks:
            raise ValidationError("Tracker has issue therefore remarks is required")
        return remarks

class LimitedTrackerChangeForm(forms.ModelForm):
    # complete_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    client_id = SearchableModelField(
        queryset=Limited.objects.all(),
        label = 'Business Name',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_viewall_url,
        repr_format = Forms.Limited_client_id_repr_format,
        model=Limited,
        choices=Limited.objects.all().only('client_id', 'client_name'),
        fk_field='client_id',
        empty_label=None,
        disabled=True
        )
    assigned_to = SearchableModelField(
        queryset=CustomUser.objects.all(),
        search_url = search_users_url_path,
        all_url = all_users_url_path,
        repr_format = Forms.CustomUser_repr_format,
        model = CustomUser,
        choices = CustomUser.objects.all().only('user_id', 'first_name'),
        fk_field = 'user_id',
        disabled = False,
        required = False,
        empty_label = None # remove default option '------' from select menu
        )
    # done_by = SearchableModelField(
    #     queryset=CustomUser.objects.all(),
    #     search_url = search_users_url_path,
    #     all_url = all_users_url_path,
    #     repr_format = Forms.CustomUser_repr_format,
    #     model = CustomUser,
    #     choices = CustomUser.objects.all().only('user_id', 'first_name'),
    #     fk_field = 'user_id',
    #     disabled = True,
    #     required = False,
    #     empty_label = None # remove default option '------' from select menu
    #     )
    
    class Meta:
        model = LimitedTracker
        fields = (
            # 'tracker_id',
            # 'created_by',
            # 'done_by',
            'assigned_to',
            'client_id',
            'job_description',
            'remarks',
            'has_issue',
            # 'complete_date',
            'is_completed',)
    
    def clean_remarks(self):
        remarks = self.cleaned_data.get('remarks').strip()
        issue = self.data.get('has_issue')
        if issue and not remarks:
            raise ValidationError("Tracker has issue therefore remarks is required")
        return remarks

class LimitedTrackerDeleteForm(forms.ModelForm):
    agree = forms.BooleanField(label='I want to proceed.', required=True)
    class Meta:
        model = Limited
        fields = ()

# Merged Tracker
class MergedTrackerCreateionForm(forms.ModelForm):
    deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'value': get_date_today, 'min': get_date_today}))
    client_id = SearchableModelField(
        queryset=Limited.objects.all(),
        label = 'Business Name/Client Name',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_viewall_url,
        repr_format = Forms.Limited_client_id_repr_format,
        model=Limited,
        choices=chain(Limited.objects.all().only('client_id', 'client_name'), Selfassesment.objects.all().only('client_id', 'client_name')),
        fk_field='client_id',
        empty_label=None
        )
    assigned_to = SearchableModelField(
        queryset=CustomUser.objects.all(),
        search_url = search_users_url_path,
        all_url = all_users_url_path,
        repr_format = Forms.CustomUser_repr_format,
        model = CustomUser,
        choices = CustomUser.objects.all().only('user_id', 'first_name'),
        fk_field = 'user_id',
        disabled = False,
        required = False,
        empty_label = None # remove default option '------' from select menu
        )
    
    class Meta:
        model = LimitedTracker
        fields = (
            # 'tracker_id',
            # 'created_by', #request.user
            # 'done_by', #request.user
            'assigned_to',
            'client_id',
            'job_description',
            'remarks',
            'has_issue',
            'deadline', #default timezone now
            # 'complete_date', #default timezone now
            # 'is_completed',
            )

    def clean_deadline(self):
        input_date = self.cleaned_data['deadline']
        current_date = timezone.now().date()
        if not input_date>=current_date:
            raise ValidationError("Deadline can't be a previous date.")
        return input_date

    def clean_remarks(self):
        remarks = self.cleaned_data.get('remarks').strip()
        issue = self.data.get('has_issue')
        if issue and not remarks:
            raise ValidationError("Tracker has issue therefore remarks is required")
        return remarks


# Limited Submission Deadline Tracker
class LimitedSubmissionDeadlineTrackerCreationForm(forms.ModelForm):
    client_id = SearchableModelField(
        queryset=Limited.objects.all(),
        label = 'Business Name',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_viewall_url,
        repr_format = Forms.Limited_client_id_repr_format,
        model=Limited,
        choices=Limited.objects.all().only('client_id', 'client_name'),
        fk_field='client_id',
        empty_label=None,
        disabled=False
        )
    # submitted_by = SearchableModelField(
    #     queryset=CustomUser.objects.all(),
    #     search_url = search_users_url_path,
    #     all_url = all_users_url_path,
    #     repr_format = Forms.CustomUser_repr_format,
    #     model = CustomUser,
    #     choices = CustomUser.objects.all().only('user_id', 'first_name'),
    #     fk_field = 'user_id',
    #     disabled = False,
    #     required = False,
    #     empty_label = None # remove default option '------' from select menu
    #     )
    # our_deadline = forms.DateField(label="HMRC deadline", widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    HMRC_deadline = forms.DateField(label="CompanyHouse Deadline", widget=forms.DateInput(attrs={'type': 'date'}))
    # submission_date_hmrc = forms.DateField(label="Submission Date(CH)", widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    # submission_date = forms.DateField(label="Submission Date(CH)", widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    period_start_date = forms.DateField(label="Period Start", widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    period = forms.DateField(label="Period End", widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    class Meta:
        model = LimitedSubmissionDeadlineTracker
        fields = (
            # "submission_id",
            "client_id",
            "status",
            "period_start_date",
            "period",
            
            # "our_deadline",
            # "is_submitted_hmrc",
            # "submitted_by_hmrc",
            # "submission_date_hmrc",

            "HMRC_deadline",
            # "is_submitted",
            # "submitted_by",
            # "submission_date",
            # "is_documents_uploaded",
            "remarks",

            # "payment_status",
            # "payment_method",
            # "paid_amount",

            # "updated_by",
            # "last_updated_on",
            )
    def clean_submission_date(self):
        is_submitted = self.cleaned_data.get('is_submitted')
        submission_date = self.cleaned_data.get('submission_date')
        if is_submitted == True and not type(submission_date)==type(date(2021, 6, 28)):
            raise ValidationError('Is Submitted is True therefore Submission Date is required.')
        return submission_date
    
    def clean(self):
        date_type = type(date(1,1,1))

        super().clean()
        period_start_date = self.cleaned_data.get("period_start_date", None)
        period = self.cleaned_data.get("period", None) # period_end_date

        if (type(period_start_date) is date_type and type(period) is not date_type) or (type(period) is date_type and type(period_start_date) is not date_type):
            message = "Period start and period end sholud be empty or both of them should be provided."
            self.add_error("period_start_date", message)
            self.add_error("period", message)
        elif type(period) is date_type and type(period_start_date) is date_type:
            date_diff = relativedelta(period+relativedelta(days=1), period_start_date)

            if not date_diff.years>=1:
                message = "Difference between period start and period and should be 1 year or more."
                self.add_error("period_start_date", message)
                self.add_error("period", message)

# Limited Submission Deadline Tracker
class LimitedSubmissionDeadlineTrackerChangeForm(forms.ModelForm):
    client_id = SearchableModelField(
        queryset=Limited.objects.all(),
        label = 'Business Name',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_viewall_url,
        repr_format = Forms.Limited_client_id_repr_format,
        model=Limited,
        choices=Limited.objects.all().only('client_id', 'client_name'),
        fk_field='client_id',
        empty_label=None,
        disabled=False
        )
    period_start_date = forms.DateField(label="Period Start", widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    period = forms.DateField(label="Period End", widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    our_deadline = forms.DateField(label="HMRC Deadline", widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    HMRC_deadline = forms.DateField(label="CompanyHouse Deadline", widget=forms.DateInput(attrs={'type': 'date'}))
    submission_date = forms.DateField(label="Submission Date(CH)", widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    submission_date_hmrc = forms.DateField(label="Submission Date(HM)", widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    class Meta:
        model = LimitedSubmissionDeadlineTracker
        fields = (
            # "submission_id",
            "client_id",
            "status",
            "period_start_date",
            "period",

            "HMRC_deadline",
            "is_submitted",
            "submission_date",
            # "submitted_by",

            "our_deadline",
            "is_submitted_hmrc",
            # "submitted_by_hmrc",
            "submission_date_hmrc",

            "is_documents_uploaded",
            "remarks",

            "payment_status",
            "payment_method",
            "paid_amount",

            # "updated_by",
            # "last_updated_on",
            )
    def clean_submission_date(self):
        is_submitted = self.cleaned_data.get('is_submitted')
        submission_date = self.cleaned_data.get('submission_date')
        if is_submitted == True and not type(submission_date)==type(date(2021, 6, 28)):
            raise ValidationError('Is Submitted is True therefore Submission Date is required.')
        return submission_date
    
    def clean_submission_date_hmrc(self):
        is_submitted = self.cleaned_data.get('is_submitted_hmrc')
        submission_date = self.cleaned_data.get('submission_date_hmrc')
        if is_submitted == True and not type(submission_date)==type(date(2021, 6, 28)):
            raise ValidationError('Is Submitted is True therefore Submission Date is required.')
        return submission_date
    
    def clean(self):
        date_type = type(date(1,1,1))

        super().clean()
        period_start_date = self.cleaned_data.get("period_start_date", None)
        period = self.cleaned_data.get("period", None) # period_end_date

        if (type(period_start_date) is date_type and type(period) is not date_type) or (type(period) is date_type and type(period_start_date) is not date_type):
            message = "Period start and period end sholud be empty or both of them should be provided."
            self.add_error("period_start_date", message)
            self.add_error("period", message)
        elif type(period) is date_type and type(period_start_date) is date_type:
            date_diff = relativedelta(period+relativedelta(days=1), period_start_date)
            
            if not date_diff.years>=1:
                message = "Difference between period start and period and should be 1 year or more."
                self.add_error("period_start_date", message)
                self.add_error("period", message)

class LimitedSubmissionDeadlineTrackerDeleteForm(forms.ModelForm):
    agree = forms.BooleanField(label='I want to proceed.', required=True)
    class Meta:
        model = LimitedSubmissionDeadlineTracker
        fields = ()


# Limited VAT Tracker
class LimitedVATTrackerCreationForm(forms.ModelForm):
    client_id = SearchableModelField(
        queryset=Limited.objects.all(),
        label = 'Business Name',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_viewall_url,
        repr_format = Forms.Limited_client_id_repr_format,
        model=Limited,
        choices=Limited.objects.all().only('client_id', 'client_name'),
        fk_field='client_id',
        empty_label=None,
        disabled=False
        )
    period_start = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    period_end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    # HMRC_deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    submission_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    class Meta:
        model = LimitedVATTracker
        fields = (
            # "vat_id",
            "client_id",
            "period_start",
            "period_end",
            # "HMRC_deadline",
            "is_submitted",
            "submitted_by",
            "submission_date",
            "is_documents_uploaded",
            "remarks",
            # "updated_by",
            # "last_updated_on",
            )

    def clean_period_end(self):
        if self.cleaned_data.get('period_start') > self.cleaned_data.get('period_end'):
            raise ValidationError("Period end can't be smaller than the period start.")
        return self.cleaned_data.get('period_end')
    
    def clean_submission_date(self):
        is_submitted = self.cleaned_data.get('is_submitted')
        submission_date = self.cleaned_data.get('submission_date')
        if is_submitted == True and not type(submission_date)==type(date(2021, 6, 28)):
            raise ValidationError('Is Submitted is True therefore Submission Date is required.')
        return submission_date

# Limited Submission Deadline Tracker
class LimitedVATTrackerChangeForm(forms.ModelForm):
    client_id = SearchableModelField(
        queryset=Limited.objects.all(),
        label = 'Business Name',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_viewall_url,
        repr_format = Forms.Limited_client_id_repr_format,
        model=Limited,
        choices=Limited.objects.all().only('client_id', 'client_name'),
        fk_field='client_id',
        empty_label=None,
        disabled=False
        )
    period_start = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    period_end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    # HMRC_deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    submission_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    class Meta:
        model = LimitedVATTracker
        fields = (
            # "vat_id",
            "client_id",
            "period_start",
            "period_end",
            # "HMRC_deadline",
            "is_submitted",
            "submitted_by",
            "submission_date",
            "is_documents_uploaded",
            "remarks",
            # "updated_by",
            # "last_updated_on",
            )
    def clean_period_end(self):
        if self.cleaned_data.get('period_start') > self.cleaned_data.get('period_end'):
            raise ValidationError("Period end can't be smaller than the period start.")
        return self.cleaned_data.get('period_end')
    
    def clean_submission_date(self):
        is_submitted = self.cleaned_data.get('is_submitted')
        submission_date = self.cleaned_data.get('submission_date')
        if is_submitted == True and not type(submission_date)==type(date(2021, 6, 28)):
            raise ValidationError('Is Submitted is True therefore Submission Date is required.')
        return submission_date

class LimitedVATTrackerDeleteForm(forms.ModelForm):
    agree = forms.BooleanField(label='I want to proceed.', required=True)
    class Meta:
        model = LimitedVATTracker
        fields = ()

# Limited Confirmation Statement Tracker
class LimitedConfirmationStatementTrackerCreationForm(forms.ModelForm):
    client_id = SearchableModelField(
        queryset=Limited.objects.all(),
        label = 'Business Name',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_viewall_url,
        repr_format = Forms.Limited_client_id_repr_format,
        model=Limited,
        choices=Limited.objects.all().only('client_id', 'client_name'),
        fk_field='client_id',
        empty_label=None,
        disabled=False
        )
    company_house_deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    submission_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    class Meta:
        model = LimitedConfirmationStatementTracker
        fields = (
            # "statement_id",
            "client_id",
            "company_house_deadline",
            "is_submitted",
            "submitted_by",
            "submission_date",
            "is_documents_uploaded",
            "remarks",
            # "updated_by",
            # "last_updated_on",
            )

    def clean_submission_date(self):
        is_submitted = self.cleaned_data.get('is_submitted')
        submission_date = self.cleaned_data.get('submission_date')
        if is_submitted == True and not type(submission_date)==type(date(2021, 6, 28)):
            raise ValidationError('Is Submitted is True therefore Submission Date is required.')
        return submission_date

# Limited Confirmation Statement Tracker
class LimitedConfirmationStatementTrackerChangeForm(forms.ModelForm):
    client_id = SearchableModelField(
        queryset=Limited.objects.all(),
        label = 'Business Name',
        search_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_search_url,
        all_url = Full_URL_PATHS_WITHOUT_ARGUMENTS.Limited_viewall_url,
        repr_format = Forms.Limited_client_id_repr_format,
        model=Limited,
        choices=Limited.objects.all().only('client_id', 'client_name'),
        fk_field='client_id',
        empty_label=None,
        disabled=False
        )
    company_house_deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    submission_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    class Meta:
        model = LimitedConfirmationStatementTracker
        fields = (
            # "statement_id",
            "client_id",
            "company_house_deadline",
            "is_submitted",
            "submitted_by",
            "submission_date",
            "is_documents_uploaded",
            "remarks",
            # "updated_by",
            # "last_updated_on",
            )

    def clean_submission_date(self):
        is_submitted = self.cleaned_data.get('is_submitted')
        submission_date = self.cleaned_data.get('submission_date')
        if is_submitted == True and not type(submission_date)==type(date(2021, 6, 28)):
            raise ValidationError('Is Submitted is True therefore Submission Date is required.')
        return submission_date

class LimitedConfirmationStatementTrackerDeleteForm(forms.ModelForm):
    agree = forms.BooleanField(label='I want to proceed.', required=True)
    class Meta:
        model = LimitedConfirmationStatementTracker
        fields = ()
