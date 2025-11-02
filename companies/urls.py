from django.urls import path
from django.urls.conf import include, re_path
from django.shortcuts import redirect

# selfassesment view functions
from .views import delete_selfassesment_data_collection, home_selfassesment, create_selfassesment, update_selfassesment, \
    delete_selfassesment, search_selfassesment, all_selfassesment, get_details_selfassesment, \
    export_selfassesment

# selfassesment data collection view functions
from .views import home_selfassesment_data_collection, create_selfassesment_data_collection,\
    update_selfassesment_data_collection, delete_selfassesment_data_collection, \
    all_selfassesment_data_collection, search_selfassesment_data_collection, export_selfassesment_data_collection, \
    auth_selfassesment_data_collection_for_client, create_selfassesment_data_collection_for_client

# selfassesment account submission tax year
from .views import search_selfassesment_account_submission_tax_year, all_selfassesment_account_submission_tax_year, \
    get_details_selfassesment_account_submission_tax_year

# selfassesment account submission view function
from .views import home_selfassesment_account_submission, create_selfassesment_account_submission, \
    update_selfassesment_account_submission, delete_selfassesment_account_submission,               \
    search_selfassesment_account_submission, all_selfassesment_account_submission,                  \
    export_selfassesment_account_submission, add_all_selfassesment_to_selfassesment_account_submission_w_submission_year

# selfassesment tracker
from .views import home_selfassesment_tracker, create_selfassesment_tracker, update_selfassesment_tracker, \
    delete_selfassesment_tracker, search_selfassesment_tracker, all_selfassesment_tracker, export_selfassesment_tracker

# limited view functions
from .views import home_limited, create_limited, update_limited, \
    delete_limited, search_limited, all_limited, get_details_limited, \
    export_limited

# limited onboarding tasks
from .views import update_limited_onboarding_tasks, search_limited_onboarding_tasks

# limited tracker
from .views import home_limited_tracker, create_limited_tracker, update_limited_tracker, \
    delete_limited_tracker, search_limited_tracker, all_limited_tracker, export_limited_tracker

# merged tracker
from .views import home_merged_tracker, create_merged_tracker, export_merged_tracker

# limited account submission view function
from .views import home_limited_submission_deadline_tracker, create_limited_submission_deadline_tracker, \
    update_limited_submission_deadline_tracker, delete_limited_submission_deadline_tracker,               \
    search_limited_submission_deadline_tracker, all_limited_submission_deadline_tracker,                  \
    export_limited_submission_deadline_tracker, info_limited_submission_deadline_tracker

# limited vat tracker
from .views import home_limited_vat_tracker, create_limited_vat_tracker, update_limited_vat_tracker, \
    delete_limited_vat_tracker, search_limited_vat_tracker, all_limited_vat_tracker, export_limited_vat_tracker

from .views import home_limited_confirmation_statement_tracker, create_limited_confirmation_statement_tracker, \
    update_limited_confirmation_statement_tracker, delete_limited_confirmation_statement_tracker, \
    search_limited_confirmation_statement_tracker, all_limited_confirmation_statement_tracker, \
    export_limited_confirmation_statement_tracker

from .url_variables import APPLICATION_NAME, URL_PATHS, URL_NAMES
from .url_variables import *


app_name = APPLICATION_NAME
application_name = app_name

urlpatterns = [
    path(route='',
        view=lambda *args, **kwargs:redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Merged_Tracker_home_name),
        name='home'),

    # =============================================================================================================
    # =============================================================================================================
    # Selfassesment
    path(route = URL_PATHS.Selfassesment_home_url,
        view = home_selfassesment,
        name = URL_NAMES.Selfassesment_home_name),

    path(route = URL_PATHS.Selfassesment_create_url,
        view = create_selfassesment,
        name = URL_NAMES.Selfassesment_create_name),

    path(route = URL_PATHS.Selfassesment_details_url,
        view = get_details_selfassesment,
        name = URL_NAMES.Selfassesment_details_name
    ),

    path(route = URL_PATHS.Selfassesment_update_url,
        view = update_selfassesment,
        name = URL_NAMES.Selfassesment_update_name),

    path(route = URL_PATHS.Selfassesment_delete_url,
        view = delete_selfassesment,
        name= URL_NAMES.Selfassesment_delete_name),

    path(route = URL_PATHS.Selfassesment_search_url,
        view = search_selfassesment,
        name = URL_NAMES.Selfassesment_search_name), # fetch only

    path(route = URL_PATHS.Selfassesment_viewall_url,
        view = all_selfassesment,
        name = URL_NAMES.Selfassesment_viewall_name), # fetch only
    
    path(route = URL_PATHS.Selfassesment_export_url,
        view = export_selfassesment,
        name = URL_NAMES.Selfassesment_export_name
    ),

    # SelfassesmentAccountSubmissionTaxYear
    path(route = URL_PATHS.Selfassesment_Account_Submission_Tax_Year_details_url,
        view = get_details_selfassesment_account_submission_tax_year,
        name = URL_NAMES.Selfassesment_Account_Submission_Tax_Year_details_name),

    path(route = URL_PATHS.Selfassesment_Account_Submission_Tax_Year_search_url,
        view = search_selfassesment_account_submission_tax_year,
        name = URL_NAMES.Selfassesment_Account_Submission_Tax_Year_search_name),

    path(route = URL_PATHS.Selfassesment_Account_Submission_Tax_Year_viewall_url,
        view = all_selfassesment_account_submission_tax_year,
        name = URL_NAMES.Selfassesment_Account_Submission_Tax_Year_viewall_name),


    # SelfassesmentAccountSubmission
    path(route = URL_PATHS.Selfassesment_Account_Submission_home_url,
        view = home_selfassesment_account_submission,
        name = URL_NAMES.Selfassesment_Account_Submission_home_name),

    path(route = URL_PATHS.Selfassesment_Account_Submission_create_url,
        view = create_selfassesment_account_submission,
        name = URL_NAMES.Selfassesment_Account_Submission_create_name),

    path(route = URL_PATHS.Selfassesment_Account_Submission_update_url,
        view = update_selfassesment_account_submission,
        name = URL_NAMES.Selfassesment_Account_Submission_update_name),

    path(route = URL_PATHS.Selfassesment_Account_Submission_delete_url,
        view = delete_selfassesment_account_submission,
        name = URL_NAMES.Selfassesment_Account_Submission_delete_name),

    path(route = URL_PATHS.Selfassesment_Account_Submission_search_url,
        view = search_selfassesment_account_submission,
        name = URL_NAMES.Selfassesment_Account_Submission_search_name),

    path(route = URL_PATHS.Selfassesment_Account_Submission_viewall_url,
        view = all_selfassesment_account_submission,
        name = URL_NAMES.Selfassesment_Account_Submission_viewall_name),
    
    path(route = URL_PATHS.Selfassesment_Account_Submission_export_url,
        view = export_selfassesment_account_submission,
        name = URL_NAMES.Selfassesment_Account_Submission_export_name
    ),

    # Add all Selfassesment to SelfassesmentAccountSubmission
    path(route = URL_PATHS.add_all_Selfassesment_to_Selfassesment_Account_Submission_url,
        view = add_all_selfassesment_to_selfassesment_account_submission_w_submission_year,
        name = URL_NAMES.add_all_Selfassesment_to_Selfassesment_Account_Submission_name),


    # =============================================================================================================
    # SelfassesmentTracker
    path(route = URL_PATHS.Selfassesment_Tracker_home_url,
        view = home_selfassesment_tracker,
        name = URL_NAMES.Selfassesment_Tracker_home_name),

    path(route = URL_PATHS.Selfassesment_Tracker_create_url,
        view = create_selfassesment_tracker,
        name = URL_NAMES.Selfassesment_Tracker_create_name),

    path(route = URL_PATHS.Selfassesment_Tracker_update_url,
        view = update_selfassesment_tracker,
        name = URL_NAMES.Selfassesment_Tracker_update_name),

    path(route = URL_PATHS.Selfassesment_Tracker_delete_url,
        view = delete_selfassesment_tracker,
        name = URL_NAMES.Selfassesment_Tracker_delete_name),

    path(route = URL_PATHS.Selfassesment_Tracker_search_url,
        view = search_selfassesment_tracker,
        name = URL_NAMES.Selfassesment_Tracker_search_name),

    path(route = URL_PATHS.Selfassesment_Tracker_viewall_url,
        view = all_selfassesment_tracker,
        name = URL_NAMES.Selfassesment_Tracker_viewall_name),
    
    path(route = URL_PATHS.Selfassesment_Tracker_export_url,
        view = export_selfassesment_tracker,
        name = URL_NAMES.Selfassesment_Tracker_export_name
    ),


    # =============================================================================================================
    # Selfassesment Data collection
    path(route = URL_PATHS.Selfassesment_Data_Collection_home_url,
        view = home_selfassesment_data_collection,
        name = URL_NAMES.Selfassesment_Data_Collection_home_name),
    
    path(route = URL_PATHS.Selfassesment_Data_Collection_create_url,
        view = create_selfassesment_data_collection,
        name = URL_NAMES.Selfassesment_Data_Collection_create_name),
    
    path(route = URL_PATHS.Selfassesment_Data_Collection_update_url,
        view = update_selfassesment_data_collection,
        name = URL_NAMES.Selfassesment_Data_Collection_update_name),
    
    path(route = URL_PATHS.Selfassesment_Data_Collection_delete_url,
        view = delete_selfassesment_data_collection,
        name = URL_NAMES.Selfassesment_Data_Collection_delete_name),
    
    path(route = URL_PATHS.Selfassesment_Data_Collection_search_url,
        view = search_selfassesment_data_collection,
        name = URL_NAMES.Selfassesment_Data_Collection_search_name),

    path(route = URL_PATHS.Selfassesment_Data_Collection_viewall_url,
        view = all_selfassesment_data_collection,
        name = URL_NAMES.Selfassesment_Data_Collection_viewall_name),

    path(route = URL_PATHS.Selfassesment_Data_Collection_export_url,
        view = export_selfassesment_data_collection,
        name = URL_NAMES.Selfassesment_Data_Collection_export_name),
    
    path(route = URL_PATHS.Selfassesment_Data_Collection_auth_url_for_client,
        view = auth_selfassesment_data_collection_for_client,
        name = URL_NAMES.Selfassesment_Data_Collection_auth_name_for_client),
    
    path(route = URL_PATHS.Selfassesment_Data_Collection_create_url_for_client,
        view = create_selfassesment_data_collection_for_client,
        name = URL_NAMES.Selfassesment_Data_Collection_create_name_for_client),

    # =============================================================================================================
    # =============================================================================================================
    # Limited
    path(route = URL_PATHS.Limited_home_url,
        view = home_limited,
        name = URL_NAMES.Limited_home_name),

    path(route = URL_PATHS.Limited_create_url,
        view = create_limited,
        name = URL_NAMES.Limited_create_name),

    path(route = URL_PATHS.Limited_details_url,
        view = get_details_limited,
        name = URL_NAMES.Limited_details_name
    ),

    path(route = URL_PATHS.Limited_update_url,
        view = update_limited,
        name = URL_NAMES.Limited_update_name),

    path(route = URL_PATHS.Limited_delete_url,
        view = delete_limited,
        name= URL_NAMES.Limited_delete_name),

    path(route = URL_PATHS.Limited_search_url,
        view = search_limited,
        name = URL_NAMES.Limited_search_name), # fetch only

    path(route = URL_PATHS.Limited_viewall_url,
        view = all_limited,
        name = URL_NAMES.Limited_viewall_name), # fetch only
    
    path(route = URL_PATHS.Limited_export_url,
        view = export_limited,
        name = URL_NAMES.Limited_export_name
    ),

    # =============================================================================================================
    # Limited Onboarding Tasks
    path(
        route = 'limited_onboarding_tasks/<int:client_id>/',
        view = update_limited_onboarding_tasks,
        name = 'limited_onboarding_tasks',
    ),
    path(
        route = 'search_limited_onboarding_tasks/',
        view = search_limited_onboarding_tasks,
        name = 'search_limited_onboarding_tasks',
    ),

    # =============================================================================================================
    # Limited Submission Deadline Tracker
    path(route = URL_PATHS.Limited_Submission_Deadline_Tracker_home_url,
        view = home_limited_submission_deadline_tracker,
        name = URL_NAMES.Limited_Submission_Deadline_Tracker_home_name),

    path(route = URL_PATHS.Limited_Submission_Deadline_Tracker_create_url,
        view = create_limited_submission_deadline_tracker,
        name = URL_NAMES.Limited_Submission_Deadline_Tracker_create_name),

    path(route = URL_PATHS.Limited_Submission_Deadline_Tracker_update_url,
        view = update_limited_submission_deadline_tracker,
        name = URL_NAMES.Limited_Submission_Deadline_Tracker_update_name),

    path(route = URL_PATHS.Limited_Submission_Deadline_Tracker_delete_url,
        view = delete_limited_submission_deadline_tracker,
        name = URL_NAMES.Limited_Submission_Deadline_Tracker_delete_name),

    path(route = URL_PATHS.Limited_Submission_Deadline_Tracker_search_url,
        view = search_limited_submission_deadline_tracker,
        name = URL_NAMES.Limited_Submission_Deadline_Tracker_search_name),

    path(route = URL_PATHS.Limited_Submission_Deadline_Tracker_viewall_url,
        view = all_limited_submission_deadline_tracker,
        name = URL_NAMES.Limited_Submission_Deadline_Tracker_viewall_name),
    
    path(route = URL_PATHS.Limited_Submission_Deadline_Tracker_export_url,
        view = export_limited_submission_deadline_tracker,
        name = URL_NAMES.Limited_Submission_Deadline_Tracker_export_name
    ),
    path(route = URL_PATHS.Limited_Submission_Deadline_Tracker_metadata_url,
        view = info_limited_submission_deadline_tracker,
        name = URL_NAMES.Limited_Submission_Deadline_Tracker_metadata_name
    ),


    # =============================================================================================================
    # LimitedTracker
    path(route = URL_PATHS.Limited_Tracker_home_url,
        view = home_limited_tracker,
        name = URL_NAMES.Limited_Tracker_home_name),

    path(route = URL_PATHS.Limited_Tracker_create_url,
        view = create_limited_tracker,
        name = URL_NAMES.Limited_Tracker_create_name),

    path(route = URL_PATHS.Limited_Tracker_update_url,
        view = update_limited_tracker,
        name = URL_NAMES.Limited_Tracker_update_name),

    path(route = URL_PATHS.Limited_Tracker_delete_url,
        view = delete_limited_tracker,
        name = URL_NAMES.Limited_Tracker_delete_name),

    path(route = URL_PATHS.Limited_Tracker_search_url,
        view = search_limited_tracker,
        name = URL_NAMES.Limited_Tracker_search_name),

    path(route = URL_PATHS.Limited_Tracker_viewall_url,
        view = all_limited_tracker,
        name = URL_NAMES.Limited_Tracker_viewall_name),
    
    path(route = URL_PATHS.Limited_Tracker_export_url,
        view = export_limited_tracker,
        name = URL_NAMES.Limited_Tracker_export_name
    ),
    
    # =============================================================================================================
    # Limited VAT Tracker
    path(route = URL_PATHS.Limited_VAT_Tracker_home_url,
        view = home_limited_vat_tracker,
        name = URL_NAMES.Limited_VAT_Tracker_home_name),

    path(route = URL_PATHS.Limited_VAT_Tracker_create_url,
        view = create_limited_vat_tracker,
        name = URL_NAMES.Limited_VAT_Tracker_create_name),

    path(route = URL_PATHS.Limited_VAT_Tracker_update_url,
        view = update_limited_vat_tracker,
        name = URL_NAMES.Limited_VAT_Tracker_update_name),

    path(route = URL_PATHS.Limited_VAT_Tracker_delete_url,
        view = delete_limited_vat_tracker,
        name = URL_NAMES.Limited_VAT_Tracker_delete_name),

    path(route = URL_PATHS.Limited_VAT_Tracker_search_url,
        view = search_limited_vat_tracker,
        name = URL_NAMES.Limited_VAT_Tracker_search_name),
    
    path(route = URL_PATHS.Limited_VAT_Tracker_viewall_url,
        view = all_limited_vat_tracker,
        name = URL_NAMES.Limited_VAT_Tracker_viewall_name),
    
    path(route = URL_PATHS.Limited_VAT_Tracker_export_url,
        view = export_limited_vat_tracker,
        name = URL_NAMES.Limited_VAT_Tracker_export_name
    ),
    
    # =============================================================================================================
    # Limited Confirmation Statement Tracker
    path(route = URL_PATHS.Limited_Confirmation_Statement_Tracker_home_url,
        view = home_limited_confirmation_statement_tracker,
        name = URL_NAMES.Limited_Confirmation_Statement_Tracker_home_name),

    path(route = URL_PATHS.Limited_Confirmation_Statement_Tracker_create_url,
        view = create_limited_confirmation_statement_tracker,
        name = URL_NAMES.Limited_Confirmation_Statement_Tracker_create_name),

    path(route = URL_PATHS.Limited_Confirmation_Statement_Tracker_update_url,
        view = update_limited_confirmation_statement_tracker,
        name = URL_NAMES.Limited_Confirmation_Statement_Tracker_update_name),

    path(route = URL_PATHS.Limited_Confirmation_Statement_Tracker_delete_url,
        view = delete_limited_confirmation_statement_tracker,
        name = URL_NAMES.Limited_Confirmation_Statement_Tracker_delete_name),

    path(route = URL_PATHS.Limited_Confirmation_Statement_Tracker_search_url,
        view = search_limited_confirmation_statement_tracker,
        name = URL_NAMES.Limited_Confirmation_Statement_Tracker_search_name),
    
    path(route = URL_PATHS.Limited_Confirmation_Statement_Tracker_viewall_url,
        view = all_limited_confirmation_statement_tracker,
        name = URL_NAMES.Limited_Confirmation_Statement_Tracker_viewall_name),
    
    path(route = URL_PATHS.Limited_Confirmation_Statement_Tracker_export_url,
        view = export_limited_confirmation_statement_tracker,
        name = URL_NAMES.Limited_Confirmation_Statement_Tracker_export_name
    ),

    # =============================================================================================================
    # Merged Tracker
    path(route = URL_PATHS.Merged_Tracker_home_url,
        view = home_merged_tracker,
        name = URL_NAMES.Merged_Tracker_home_name
    ),

    path(route = URL_PATHS.Merged_Tracker_create_url,
        view = create_merged_tracker,
        name = URL_NAMES.Merged_Tracker_create_name),

    path(route = URL_PATHS.Merged_Tracker_export_url,
        view = export_merged_tracker,
        name = URL_NAMES.Merged_Tracker_export_name
    )
]
