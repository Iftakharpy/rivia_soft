from datetime import date, datetime
from itertools import chain
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .fields import SearchableModelField, Select, Fieldset
from .url_variables import Full_URL_PATHS_WITHOUT_ARGUMENTS

from .models import Selfassesment, SelfassesmentAccountSubmission, SelfassesmentTracker, SelfassesmentAccountSubmissionTaxYear
from .models import Limited, LimitedTracker, LimitedSubmissionDeadlineTracker, LimitedVATTracker, LimitedConfirmationStatementTracker

# from .queries import db_all_Limited, db_all_LimitedConfirmationStatementTracker, db_all_LimitedSubmissionDeadlineTracker, \
#     db_all_LimitedTracker, db_all_LimitedVATTracker
# from .queries import db_all_Selfassesment, db_all_SelfassesmentAccountSubmission, db_all_SelfassesmentAccountSubmissionTaxYear, \
#     db_all_SelfassesmentTracker

from .repr_formats import Forms

# dummy import
# uncomment next line before migrating
# from .dummy_class import *


from users.models import CustomUser
search_users_url_path = '/u/search/'
all_users_url_path = '/u/all/'


def get_date_today(date_format = '%Y-%m-%d'):
    today = timezone.datetime.strftime(timezone.now(), date_format)
    return today

class SelfassesmentCreationForm(forms.ModelForm):
    date_of_registration = forms.DateField(
        label='Registration date',
        widget=forms.DateInput(attrs={'type': 'date', 'value': get_date_today, 'placehoder': 'Registration date'})
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date',})
    )

    class Meta:
        model = Selfassesment
        fields = (
            # 'client_id',
            # 'created_by',
            # 'is_updated',
            'selfassesment_type',
            'date_of_registration',
            'is_active',
            'remarks',

            'client_file_number',
            'client_name',

            'date_of_birth',
            'PAYE_number',
            'personal_phone_number',
            'personal_email',
            'personal_address',
            'personal_post_code',

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
                fields = ('client_file_number', 'selfassesment_type', 'date_of_registration', 'client_name', 'remarks', 'is_active', )
                ),
            Fieldset(
                title = 'Personal Info',
                fields = ('date_of_birth', 'personal_phone_number', 'personal_email', 'personal_address', 'personal_post_code', )
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


class SelfassesmentChangeForm(forms.ModelForm):
    date_of_registration = forms.DateField(
        label='Registration date',
        widget=forms.DateInput(attrs={'type': 'date', 'value': get_date_today, 'placehoder': 'Registration date'})
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date',})
    )
    
    class Meta:
        model = Selfassesment
        fields = (
            # 'client_id',
            # 'created_by',
            # 'is_updated',
            'selfassesment_type',
            'date_of_registration',
            'is_active',
            'remarks',

            'client_file_number',
            'client_name',

            'date_of_birth',
            'PAYE_number',
            'personal_phone_number',
            'personal_email',
            'personal_address',
            'personal_post_code',

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
                fields = ('client_file_number', 'selfassesment_type', 'date_of_registration', 'client_name', 'remarks', 'is_active', )
                ),
            Fieldset(
                title = 'Personal Info',
                fields = ('date_of_birth', 'personal_phone_number', 'personal_email', 'personal_address', 'personal_post_code', )
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

class SelfassesmentDeleteForm(forms.ModelForm):
    agree = forms.BooleanField(label='I want to proceed.', required=True)
    class Meta:
        model = Selfassesment
        fields = ()


class SelfassesmentAccountSubmissionCreationForm(forms.ModelForm):
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
            "client_id",
            "status",
            "appointment_date",
            "tax_year",
            "request_date",
            "remarks",
            "payment_status",
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
    request_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = SelfassesmentAccountSubmission
        fields = (
            # "submission_id",
            "client_id",
            "status",
            "appointment_date",
            # "request_date",
            "tax_year",
            "remarks",
            "payment_status",
            "paid_amount",
            "prepared_by",
            # "submitted_by",
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
            'date_of_registration',
            'is_active',
            'remarks',

            'client_file_number',
            'client_name',
            'company_reg_number',
            'company_auth_code',

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
                fields = ('client_file_number', 'date_of_registration', 'client_name', 'company_reg_number', 'company_auth_code', 'remarks', 'is_active', )
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
            'date_of_registration',
            'is_active',
            'remarks',

            'client_file_number',
            'client_name',
            'company_reg_number',
            'company_auth_code',

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
                fields = ('client_file_number', 'date_of_registration', 'client_name', 'company_reg_number', 'company_auth_code', 'remarks', 'is_active', )
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

class LimitedDeleteForm(forms.ModelForm):
    agree = forms.BooleanField(label='I want to proceed.', required=True)
    class Meta:
        model = Limited
        fields = ()

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
    our_deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    HMRC_deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    submission_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    class Meta:
        model = LimitedSubmissionDeadlineTracker
        fields = (
            # "submission_id",
            "client_id",
            "period",
            "our_deadline",
            "HMRC_deadline",
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
    our_deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    HMRC_deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    submission_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    class Meta:
        model = LimitedSubmissionDeadlineTracker
        fields = (
            # "submission_id",
            "client_id",
            "period",
            "our_deadline",
            "HMRC_deadline",
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
    HMRC_deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    submission_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    class Meta:
        model = LimitedConfirmationStatementTracker
        fields = (
            # "statement_id",
            "client_id",
            "HMRC_deadline",
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
    HMRC_deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    submission_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    class Meta:
        model = LimitedConfirmationStatementTracker
        fields = (
            # "statement_id",
            "client_id",
            "HMRC_deadline",
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
