from django.urls import path

from .views import index, get_all_expense_sources, get_all_income_sources, get_all_deduction_sources, get_all_taxable_income_sources, get_all_months, upsert_deduction_for_submission, upsert_expese_for_submission, upsert_income_for_submission, get_expenses_for_submission, get_incomes_for_submission, get_deductions_for_submission, get_taxable_incomes_for_submission



urlpatterns = [
    path("", index),
    
    # update or set data
    path("set_income/<int:submission_id>/<int:month_id>/<int:income_id>/", upsert_income_for_submission),
    path("set_expense/<int:submission_id>/<int:month_id>/<int:expense_id>/", upsert_expese_for_submission),
    path("set_deduction/<int:submission_id>/<int:deduction_id>/", upsert_deduction_for_submission),

    # get data
    path("income_sources/", get_all_income_sources),
    path("expense_sources/", get_all_expense_sources),
    path("deduction_sources/", get_all_deduction_sources),
    path("taxable_income_sources/", get_all_taxable_income_sources),
    path("months/", get_all_months),

    path("incomes/<int:submission_id>/", get_incomes_for_submission),
    path("expenses/<int:submission_id>/", get_expenses_for_submission),
    path("deductions/<int:submission_id>/", get_deductions_for_submission),
    path("taxable_incomes/<int:submission_id>/", get_taxable_incomes_for_submission),
]
