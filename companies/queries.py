from django.db.models import Q
from .models import Selfassesment, SelfassesmentAccountSubmission, SelfassesmentTracker, SelfassesmentAccountSubmissionTaxYear, SelfemploymentIncomeAndExpensesDataCollection
from .models import Limited, LimitedTracker, LimitedSubmissionDeadlineTracker, LimitedVATTracker, LimitedConfirmationStatementTracker
from datetime import date, datetime
from django.utils import timezone
from itertools import chain

# =============================================================================================================
# =============================================================================================================
# Selfassesment
def db_search_Selfassesment(search_text: str, limit=-1):
    Query = Q(client_file_number__icontains            = search_text) |\
            Q(selfassesment_type__type_name__icontains = search_text) |\
            Q(date_of_registration__icontains          = search_text) |\
            Q(remarks__icontains                       = search_text) |\
            Q(client_name__icontains                   = search_text) |\
            Q(date_of_birth__icontains                 = search_text) |\
            Q(PAYE_number__icontains                   = search_text) |\
            Q(personal_phone_number__icontains         = search_text) |\
            Q(personal_email__icontains                = search_text) |\
            Q(personal_address__icontains              = search_text) |\
            Q(personal_post_code__icontains            = search_text) |\
            Q(AOR_number__icontains                    = search_text) |\
            Q(business_phone_number__icontains         = search_text) |\
            Q(business_email__icontains                = search_text) |\
            Q(business_address__icontains              = search_text) |\
            Q(business_post_code__icontains            = search_text) |\
            Q(HMRC_agent__icontains                    = search_text) |\
            Q(HMRC_referance__icontains                = search_text) |\
            Q(UTR__icontains                           = search_text) |\
            Q(NINO__icontains                          = search_text) |\
            Q(gateway_id__icontains                    = search_text) |\
            Q(gateway_password__icontains              = search_text) |\
            Q(bank_name__icontains                     = search_text) |\
            Q(bank_account_number__icontains           = search_text) |\
            Q(bank_sort_code__icontains                = search_text) |\
            Q(bank_account_holder_name__icontains      = search_text)

    try:
        num = int(search_text)
        Query |= Q(client_id          = num)
    except Exception:
        pass
    
    if limit==-1:
        return Selfassesment.objects.filter(Query)
    return Selfassesment.objects.filter(Query)[:limit]

def db_all_Selfassesment(limit=-1):
    result = Selfassesment.objects.filter(is_active=True)
    if limit<=-1:
        return result
    return result[:limit]


# SelfemploymentIncomeAndExpensesDataCollection
def db_search_SelfemploymentIncomeAndExpensesDataCollection(search_text: str, limit=-1):
    Query = Q(selfassesment__selfassesment_type__type_name__icontains = search_text) |\
            Q(selfassesment__date_of_registration__icontains          = search_text) |\
            Q(selfassesment__remarks__icontains                       = search_text) |\
            Q(selfassesment__client_name__icontains                   = search_text) |\
            Q(selfassesment__date_of_birth__icontains                 = search_text) |\
            Q(selfassesment__PAYE_number__icontains                   = search_text) |\
            Q(selfassesment__personal_phone_number__icontains         = search_text) |\
            Q(selfassesment__personal_email__icontains                = search_text) |\
            Q(selfassesment__personal_address__icontains              = search_text) |\
            Q(selfassesment__personal_post_code__icontains            = search_text) |\
            Q(selfassesment__AOR_number__icontains                    = search_text) |\
            Q(selfassesment__business_phone_number__icontains         = search_text) |\
            Q(selfassesment__business_email__icontains                = search_text) |\
            Q(selfassesment__business_address__icontains              = search_text) |\
            Q(selfassesment__business_post_code__icontains            = search_text) |\
            Q(selfassesment__HMRC_agent__icontains                    = search_text) |\
            Q(selfassesment__HMRC_referance__icontains                = search_text) |\
            Q(selfassesment__UTR__icontains                           = search_text) |\
            Q(selfassesment__NINO__icontains                          = search_text) |\
            Q(selfassesment__gateway_id__icontains                    = search_text) |\
            Q(selfassesment__gateway_password__icontains              = search_text) |\
            Q(selfassesment__bank_name__icontains                     = search_text) |\
            Q(selfassesment__bank_account_number__icontains           = search_text) |\
            Q(selfassesment__bank_sort_code__icontains                = search_text) |\
            Q(selfassesment__bank_account_holder_name__icontains      = search_text)

    Query |= Q(tax_year__tax_year__icontains = search_text)

    try:
        num = int(search_text)
        Query |= Q(selfassesment__client_id          = num) |\
                 Q(selfassesment__client_file_number = num)
    except Exception:
        pass
    
    if limit==-1:
        return SelfemploymentIncomeAndExpensesDataCollection.objects.filter(Query)
    return SelfemploymentIncomeAndExpensesDataCollection.objects.filter(Query)[:limit]

def db_all_SelfemploymentIncomeAndExpensesDataCollection(limit=-1):
    if limit<=-1:
        return SelfemploymentIncomeAndExpensesDataCollection.objects.filter()
    return SelfemploymentIncomeAndExpensesDataCollection.objects.filter()[:limit]


# SelfassesmentAccountSubmissionTaxYear
def db_search_SelfassesmentAccountSubmissionTaxYear(search_text:str, limit=-1):
    Query = Q(tax_year__icontains = search_text)
    try:
        num = int(search_text)
        Query |= Q(id = num)
    except Exception:
        pass

    records = SelfassesmentAccountSubmissionTaxYear.objects.filter(Query)
    if limit==-1:
        return records
    return records[:limit]

def db_all_SelfassesmentAccountSubmissionTaxYear(limit=-1):
    records = SelfassesmentAccountSubmissionTaxYear.objects.all()
    if limit<=-1:
        return records
    return records[:limit]

# SelfassesmentAccountSubmission
def db_search_SelfassesmentAccountSubmission(search_text: str, limit=-1):
    Query = Q(request_date__icontains                     = search_text) |\
            Q(appointment_date__icontains                 = search_text) |\
            Q(status__icontains                           = search_text) |\
            Q(payment_status__iexact                      = search_text) |\
            Q(tax_year__tax_year__icontains               = search_text) |\
            Q(client_id__client_name__icontains           = search_text) |\
            Q(client_id__personal_phone_number__icontains = search_text) |\
            Q(client_id__business_phone_number__icontains = search_text) |\
            Q(submitted_by__email__icontains              = search_text) |\
            Q(submitted_by__first_name__icontains         = search_text) |\
            Q(submitted_by__last_name__icontains          = search_text) |\
            Q(prepared_by__email__icontains               = search_text) |\
            Q(prepared_by__first_name__icontains          = search_text) |\
            Q(prepared_by__last_name__icontains           = search_text) |\
            Q(last_updated_by__email__icontains           = search_text) |\
            Q(last_updated_by__first_name__icontains      = search_text) |\
            Q(last_updated_by__last_name__icontains       = search_text) |\
            Q(remarks__icontains                          = search_text)
    try:
        num = int(search_text)
        Query |= Q(submission_id                = num) |\
                Q(client_id__client_file_number = num) |\
                Q(client_id                     = num) |\
                Q(paid_amount                   = num)
    except Exception:
        pass
    records = SelfassesmentAccountSubmission.objects.filter(Query)
    if limit==-1:
        return records
    return records[:limit]


def db_all_SelfassesmentAccountSubmission(limit=-1):
    # records = SelfassesmentAccountSubmission.objects.filter(tax_year=SelfassesmentAccountSubmissionTaxYear.get_max_year())
    records = SelfassesmentAccountSubmission.objects.all()
    if limit<=-1:
        return records
    return records[:limit]


# =============================================================================================================
# =============================================================================================================
# SelfassesmentTracker
def db_search_SelfassesmentTracker(search_text: str, user_email='', is_superuser=False, limit=-1):
    Query = Q(job_description__icontains                  = search_text) |\
            Q(deadline__icontains                         = search_text) |\
            Q(client_id__client_name__icontains           = search_text) |\
            Q(client_id__personal_phone_number__icontains = search_text) |\
            Q(client_id__business_phone_number__icontains = search_text) |\
            Q(client_id__client_file_number__icontains    = search_text) |\
            Q(created_by__first_name__icontains           = search_text) |\
            Q(created_by__last_name__icontains            = search_text) |\
            Q(done_by__first_name__icontains              = search_text) |\
            Q(done_by__last_name__icontains               = search_text)
    
    # # created by should be the current logged in user
    # if not is_superuser:
    #     Query &= Q(created_by__email = user_email)
    
    # Filter records from db using query
    if limit==-1:
        records = SelfassesmentTracker.objects.filter(Query)
    else:
        records = SelfassesmentTracker.objects.filter(Query)[:limit]
    return records

def db_all_SelfassesmentTracker(user_email='', is_superuser=False, limit=-1):
    Query = Q(is_completed=False)
    # # created by should be the current logged in user
    # if not is_superuser:
    #     Query = Query & Q(created_by__email = user_email)
    
    if limit==-1:
        records = SelfassesmentTracker.objects.filter(Query)
    else:
        records = SelfassesmentTracker.objects.filter(Query)[:limit]
    return records



# =============================================================================================================
# =============================================================================================================
# Limited
def db_search_Limited(search_text: str, limit=-1):
    Query = Q(client_file_number__icontains            = search_text) |\
            Q(date_of_registration__icontains          = search_text) |\
            Q(remarks__icontains                       = search_text) |\
            Q(client_name__icontains                   = search_text) |\
            Q(company_reg_number__icontains            = search_text) |\
            Q(company_auth_code__icontains             = search_text) |\
            Q(date_of_birth__icontains                 = search_text) |\
            Q(PAYE_number__icontains                   = search_text) |\
            Q(director_phone_number__icontains         = search_text) |\
            Q(director_email__icontains                = search_text) |\
            Q(director_address__icontains              = search_text) |\
            Q(director_post_code__icontains            = search_text) |\
            Q(AOR_number__icontains                    = search_text) |\
            Q(business_phone_number__icontains         = search_text) |\
            Q(business_email__icontains                = search_text) |\
            Q(business_address__icontains              = search_text) |\
            Q(business_post_code__icontains            = search_text) |\
            Q(HMRC_agent__icontains                    = search_text) |\
            Q(HMRC_referance__icontains                = search_text) |\
            Q(UTR__icontains                           = search_text) |\
            Q(NINO__icontains                          = search_text) |\
            Q(vat__icontains                           = search_text) |\
            Q(gateway_id__icontains                    = search_text) |\
            Q(gateway_password__icontains              = search_text) |\
            Q(bank_name__icontains                     = search_text) |\
            Q(bank_account_number__icontains           = search_text) |\
            Q(bank_sort_code__icontains                = search_text) |\
            Q(bank_account_holder_name__icontains      = search_text)

    try:
        num = float(search_text)
        Query |= Q(client_id          = num)
    except Exception:
        pass
    
    if limit==-1:
        return Limited.objects.filter(Query)
    return Limited.objects.filter(Query)[:limit]

def db_all_Limited(limit=-1):
    result = Limited.objects.filter(is_active=True)
    if limit<=-1:
        return result
    return result[:limit]


# =============================================================================================================
# =============================================================================================================
# LimitedTracker
def db_search_LimitedTracker(search_text: str, user_email='', is_superuser=False, limit=-1):
    Query = Q(job_description__icontains                  = search_text) |\
            Q(deadline__icontains                         = search_text) |\
            Q(client_id__client_name__icontains           = search_text) |\
            Q(client_id__director_phone_number__icontains = search_text) |\
            Q(client_id__business_phone_number__icontains = search_text) |\
            Q(client_id__company_reg_number__icontains               = search_text) |\
            Q(client_id__client_file_number__icontains    = search_text) |\
            Q(created_by__first_name__icontains           = search_text) |\
            Q(created_by__last_name__icontains            = search_text) |\
            Q(done_by__first_name__icontains              = search_text) |\
            Q(done_by__last_name__icontains               = search_text)
    
    # # created by should be the current logged in user
    # if not is_superuser:
    #     Query &= Q(created_by__email = user_email)
    
    # Filter records from db using query
    if limit==-1:
        records = LimitedTracker.objects.filter(Query)
    else:
        records = LimitedTracker.objects.filter(Query)[:limit]
    return records

def db_all_LimitedTracker(user_email='', is_superuser=False, limit=-1):
    Query = Q(is_completed=False)
    # # created by should be the current logged in user
    # if not is_superuser:
    #     Query = Query & Q(created_by__email = user_email)
    
    if limit==-1:
        records = LimitedTracker.objects.filter(Query)
    else:
        records = LimitedTracker.objects.filter(Query)[:limit]
    return records

# LimitedSubmissionDeadlineTracker
def db_search_LimitedSubmissionDeadlineTracker(search_text: str, limit=-1):
    Query = Q(period__icontains                             = search_text) |\
            Q(our_deadline__icontains                       = search_text) |\
            Q(client_id__client_name__icontains             = search_text) |\
            Q(client_id__director_phone_number__icontains   = search_text) |\
            Q(client_id__director_post_code__icontains      = search_text) |\
            Q(client_id__company_reg_number__icontains      = search_text) |\
            Q(HMRC_deadline__icontains                      = search_text) |\
            Q(submission_date__icontains                    = search_text) |\
            Q(remarks__icontains                            = search_text) |\
            Q(last_updated_on__icontains                    = search_text) |\
            Q(is_submitted__icontains                       = search_text) |\
            Q(updated_by__email__icontains                  = search_text) |\
            Q(updated_by__first_name__icontains             = search_text) |\
            Q(updated_by__last_name__icontains              = search_text) |\
            Q(is_documents_uploaded__icontains              = search_text)
    try:
        num = float(search_text)
        Query |= Q(submission_id                = int(num)) |\
                Q(client_id__client_file_number = num)
    except Exception:
        pass

    return LimitedSubmissionDeadlineTracker.ordered_manager.ordered_filter(Query)

    # upcoming = LimitedSubmissionDeadlineTracker.ordered_manager.ordered_upcoming_all().filter(Query)
    # previous = LimitedSubmissionDeadlineTracker.ordered_manager.ordered_previous_all().filter(Query)
    # return chain(upcoming, previous)


def db_all_LimitedSubmissionDeadlineTracker(limit=-1):
    return LimitedSubmissionDeadlineTracker.ordered_manager.ordered_all()
    # upcoming = LimitedSubmissionDeadlineTracker.ordered_manager.ordered_upcoming_all()
    # previous = LimitedSubmissionDeadlineTracker.ordered_manager.ordered_previous_all()
    # return chain(upcoming, previous)


# LimitedVATTracker
def db_search_LimitedVATTracker(search_text: str, limit=-1):
    Query = Q(client_id__client_name__icontains               = search_text) |\
            Q(client_id__director_phone_number__icontains               = search_text) |\
            Q(client_id__company_reg_number__icontains               = search_text) |\
            Q(client_id__director_post_code__icontains               = search_text) |\
            Q(period_start__icontains              = search_text) |\
            Q(period_end__icontains              = search_text) |\
            Q(HMRC_deadline__icontains              = search_text) |\
            Q(submission_date__icontains            = search_text) |\
            Q(remarks__icontains                    = search_text) |\
            Q(last_updated_on__icontains            = search_text)|\
            Q(is_submitted__icontains               = search_text) |\
            Q(updated_by__email__icontains          = search_text) |\
            Q(updated_by__first_name__icontains     = search_text) |\
            Q(updated_by__last_name__icontains      = search_text) |\
            Q(is_documents_uploaded__icontains      = search_text)
    try:
        num = float(search_text)
        Query |= Q(vat_id                = int(num)) |\
                Q(client_id__client_file_number = num)
    except Exception:
        pass
    
    if limit==-1:
        return LimitedVATTracker.objects.filter(Query)
    return LimitedVATTracker.objects.filter(Query)[:limit]


def db_all_LimitedVATTracker(limit=-1):
    records = LimitedVATTracker.objects.filter(HMRC_deadline__gte = timezone.now()).order_by('HMRC_deadline')
    other_records = LimitedVATTracker.objects.filter().exclude(HMRC_deadline__gte = timezone.now())
    records = chain(records, other_records)
    if limit<=-1:
        return records
    return records[:limit]

# LimitedConfirmationStatementTracker
def db_search_LimitedConfirmationStatementTracker(search_text: str, limit=-1):
    Query = Q(client_id__client_name__icontains               = search_text) |\
            Q(client_id__director_phone_number__icontains               = search_text) |\
            Q(client_id__director_post_code__icontains               = search_text) |\
            Q(client_id__company_reg_number__icontains               = search_text) |\
            Q(company_house_deadline__icontains              = search_text) |\
            Q(submission_date__icontains            = search_text) |\
            Q(remarks__icontains                    = search_text) |\
            Q(last_updated_on__icontains            = search_text)|\
            Q(is_submitted__icontains               = search_text) |\
            Q(updated_by__email__icontains          = search_text) |\
            Q(updated_by__first_name__icontains     = search_text) |\
            Q(updated_by__last_name__icontains      = search_text) |\
            Q(is_documents_uploaded__icontains      = search_text)
    try:
        num = float(search_text)
        Query |= Q(statement_id                = int(num)) |\
                Q(client_id__client_file_number = num)
    except Exception:
        pass
    
    return LimitedConfirmationStatementTracker.ordered_manager.ordered_filter(Query)


def db_all_LimitedConfirmationStatementTracker(limit=-1):
    return LimitedConfirmationStatementTracker.ordered_manager.ordered_all()
