from typing import Type
from django.db import models
from .utils import is_includeable, get_field_names_from_model, get_header_name_from_field_name

from .url_variables import URL_PATHS, URL_NAMES, Full_URL_PATHS_WITHOUT_ARGUMENTS, URL_NAMES_PREFIXED_WITH_APP_NAME
from .repr_formats import HTML_Generator


ModelClass = Type[models.Model] 

# foreign key fields
user_details_url_without_argument = '/u/details/'

def generate_template_tag_for_model(
    django_model: ModelClass,
    pk_field = 'id',
    exclude_fields = [],
    include_fields = [],
    extra_fields = [],
    ordering = [],
    keep_include_fields = True,
    show_others = True,
    show_id = True,
    tag_name = 'data-template',
    tag_id = 'data-template',
    fk_fields = {
      'last_updated_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'created_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'issue_created_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'done_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'submitted_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'submitted_by_hmrc': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'prepared_by': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'assigned_to': { 'details_url_without_argument': user_details_url_without_argument, 'repr-format': HTML_Generator.CustomUser_repr_format },
      'client_id': { 'details_url_without_argument': Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_details_url, 'repr-format': HTML_Generator.Selfassesment_client_id_repr_format, 'href-url':Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_update_url },
      'selfassesment': { 'details_url_without_argument': Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_details_url, 'repr-format': HTML_Generator.Selfassesment_client_id_repr_format, 'href-url':Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_update_url },
      'tax_year': { 'details_url_without_argument': Full_URL_PATHS_WITHOUT_ARGUMENTS.Selfassesment_Account_Submission_Tax_Year_details_url, 'repr-format': HTML_Generator.Selfassemsent_tax_year_repr_format },
      'incomplete_tasks': { 'details_url_without_argument': '/companies/SATrc/search/?client_id=', 'repr-format': r'{length}', 'data-field': 'pk', 'href-url':'/companies/SATrc/home/?client_id='},
      'company_registration_number': { 'details_url_without_argument': '/companies/LTD/details/', 'repr-format': r'{company_reg_number}', 'data-field': 'fields.client_id'},
      'invoice_from': { 'details_url_without_argument': '/invoice/companies/', 'repr-format': r'{formatted}', 'data-url-ending': '/formatted/', 'href-url': r'/invoice/companies/{fields.invoice_from}/redirect_to_original/' },
      'invoice_to': { 'details_url_without_argument': '/invoice/companies/', 'repr-format': r'{formatted}', 'data-url-ending': '/formatted/', 'href-url': r'/invoice/companies/{fields.invoice_to}/redirect_to_original/' },
      'invoice_reference_id': { 'details_url_without_argument': '/invoice/invoices/', 'repr-format': r"{formatted}", 'data-url-ending': '/formatted/', 'href-url': r'/invoice/invoices/{fields.invoice_reference_id}/update_form/' },
      'transaction_from': { 'details_url_without_argument': '/invoice/companies/', 'repr-format': r'{formatted}', 'data-url-ending': '/formatted/', 'href-url': r'/invoice/companies/{fields.transaction_from}/redirect_to_original/' },
      'all_transactions': { 'details_url_without_argument': '/invoice/companies/', 'data-field': 'fields.transaction_from', 'repr-format': r'All transaction from company', 'data-url-ending': '/formatted/', 'href-url': r'/invoice/transactions/{fields.transaction_from}/view_all_transactions_of_company/' },
      'all_onboarding_tasks': { 'details_url_without_argument': '/companies/search_limited_onboarding_tasks/?tasks=__all__&count_only=True&client_id=', 'repr-format': r'Total {all_tasks} tasks', 'data-field': 'pk', 'href-url':'/companies/limited_onboarding_tasks/{pk}/'},
      'onboarding_tasks__status__Done': { 'details_url_without_argument': '/companies/search_limited_onboarding_tasks/?tasks=__all__&count_only=True&client_id=', 'repr-format': r'Done {status__Done} tasks', 'data-field': 'pk', 'href-url':'/companies/limited_onboarding_tasks/{pk}/'},
      'onboarding_tasks__status__In_Progress': { 'details_url_without_argument': '/companies/search_limited_onboarding_tasks/?tasks=__all__&count_only=True&client_id=', 'repr-format': r'In Progress {status__InProgress} tasks', 'data-field': 'pk', 'href-url':'/companies/limited_onboarding_tasks/{pk}/'},
      'onboarding_tasks__status__Need_to_do': { 'details_url_without_argument': '/companies/search_limited_onboarding_tasks/?tasks=__all__&count_only=True&client_id=', 'repr-format': r'Need to do {status__NeedToDo} tasks', 'data-field': 'pk', 'href-url':'/companies/limited_onboarding_tasks/{pk}/'},
      'onboarding_tasks__status__Not_Applicable': { 'details_url_without_argument': '/companies/search_limited_onboarding_tasks/?tasks=__all__&count_only=True&client_id=', 'repr-format': r'Not applicable {status__NotApplicable} tasks', 'data-field': 'pk', 'href-url':'/companies/limited_onboarding_tasks/{pk}/'},
    },
  ):
  inner_template_tr = """
  <td class="data-cell data-id" >
    <a class="w-max" href="" id='edit'>
      <svg class="edit-icon" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
        viewBox="0 0 512 512" style="enable-background:new 0 0 512 512;" xml:space="preserve">
      <g>
        <g>
          <g>
            <path d="M352.459,220c0-11.046-8.954-20-20-20h-206c-11.046,0-20,8.954-20,20s8.954,20,20,20h206
              C343.505,240,352.459,231.046,352.459,220z"/>
            <path d="M126.459,280c-11.046,0-20,8.954-20,20c0,11.046,8.954,20,20,20H251.57c11.046,0,20-8.954,20-20c0-11.046-8.954-20-20-20
              H126.459z"/>
            <path d="M173.459,472H106.57c-22.056,0-40-17.944-40-40V80c0-22.056,17.944-40,40-40h245.889c22.056,0,40,17.944,40,40v123
              c0,11.046,8.954,20,20,20c11.046,0,20-8.954,20-20V80c0-44.112-35.888-80-80-80H106.57c-44.112,0-80,35.888-80,80v352
              c0,44.112,35.888,80,80,80h66.889c11.046,0,20-8.954,20-20C193.459,480.954,184.505,472,173.459,472z"/>
            <path d="M467.884,289.572c-23.394-23.394-61.458-23.395-84.837-0.016l-109.803,109.56c-2.332,2.327-4.052,5.193-5.01,8.345
              l-23.913,78.725c-2.12,6.98-0.273,14.559,4.821,19.78c3.816,3.911,9,6.034,14.317,6.034c1.779,0,3.575-0.238,5.338-0.727
              l80.725-22.361c3.322-0.92,6.35-2.683,8.79-5.119l109.573-109.367C491.279,351.032,491.279,312.968,467.884,289.572z
              M333.776,451.768l-40.612,11.25l11.885-39.129l74.089-73.925l28.29,28.29L333.776,451.768z M439.615,346.13l-3.875,3.867
              l-28.285-28.285l3.862-3.854c7.798-7.798,20.486-7.798,28.284,0C447.399,325.656,447.399,338.344,439.615,346.13z"/>
            <path d="M332.459,120h-206c-11.046,0-20,8.954-20,20s8.954,20,20,20h206c11.046,0,20-8.954,20-20S343.505,120,332.459,120z"/>
          </g>
        </g>
      </g>
      </svg>
    <a class="w-max" href="" id='delete'>
      <svg class="delete-icon" enable-background="new 0 0 512.016 512.016" height="512" viewBox="0 0 512.016 512.016" width="512" xmlns="http://www.w3.org/2000/svg">
        <g>
          <path d="m448.199 164.387h-236.813l106.048-106.048c5.858-5.858 5.858-15.356 0-21.215l-26.872-26.872c-13.669-13.669-35.831-13.669-49.501 0l-27.63 27.631-14.144-14.144c-15.596-15.597-40.975-15.596-56.572 0l-55.158 55.158c-15.597 15.597-15.597 40.976 0 56.573l14.143 14.144-27.63 27.63c-13.669 13.669-13.669 35.831 0 49.501l26.872 26.872c5.857 5.858 15.356 5.859 21.214 0l38.021-38.021v231.416c0 35.901 29.104 65.005 65.005 65.005h158.012c35.901 0 65.005-29.104 65.005-65.005zm-325.284-35.989-14.143-14.143c-3.899-3.899-3.899-10.244 0-14.144l55.158-55.158c3.9-3.9 10.245-3.899 14.143 0l14.143 14.144zm129.533 299.612c0 8.285-6.716 15.001-15.001 15.001s-15.001-6.716-15.001-15.001v-179.616c0-8.285 6.716-15.001 15.001-15.001s15.001 6.716 15.001 15.001zm66.741 0c0 8.285-6.716 15.001-15.001 15.001s-15.001-6.716-15.001-15.001v-179.616c0-8.285 6.716-15.001 15.001-15.001s15.001 6.716 15.001 15.001zm66.741 0c0 8.285-6.716 15.001-15.001 15.001s-15.001-6.716-15.001-15.001v-179.616c0-8.285 6.716-15.001 15.001-15.001s15.001 6.716 15.001 15.001z"/>
          <path d="m320.898 113.548c-9.151 3.19-15.571 11.361-16.631 20.842h143.932v-24.932c0-17.119-16.845-29.167-33.022-23.682l-93.968 27.672c-.101.029-.211.069-.311.1z"/>
        </g>
      </svg>
    </a>
  </td>
  """
  # mantain field order
  model_fields = get_field_names_from_model(django_model)
  field_order = list(ordering) # provided order
  for field in include_fields: # include_field order
    if field not in field_order:
      field_order.append(field)
  for field in model_fields: # django model's order
    if field not in field_order:
      field_order.append(field)

  for field in field_order:
    # skip if field is pk_field
    if field is pk_field or not is_includeable(field, include_fields, exclude_fields, keep_include_fields, show_others):
      if show_id and pk_field==field:
        inner_template_tr += f'<td class="data-cell" id="pk"></td>\n'
      continue
    
    if field in fk_fields:
      data_attrs = f"""
        data-url="{fk_fields[field]['details_url_without_argument']}" 
        data-repr-format="{fk_fields[field]['repr-format']}" 
        """
      if fk_fields[field].get('data-field'):
        data_attrs += f'''
          data-field="{fk_fields[field].get('data-field')}"
        '''
      else:
        data_attrs += f'''
          data-field="fields.{field}"
        '''
      if fk_fields[field].get('href-url'):
        data_attrs += f'''data-href-url="{fk_fields[field]['href-url']}"'''
      if fk_fields[field].get('data-url-ending'):
        data_attrs += f'''data-url-ending="{fk_fields[field]['data-url-ending']}"'''

      inner_template_tr+=f"""
      <td class="data-cell" id="{field}"
        {data_attrs}></td>\n"""
    
    else:
      inner_template_tr += f'<td class="data-cell" id="{field}"></td>\n'
  
  template_tag = f"""
  <template id="{tag_id}" name="{tag_name}">
    <tr class="data-row">
    {inner_template_tr}
    </tr>
  </template>
  """
  return template_tag


def generate_data_container_table(
    django_model: ModelClass,
    pk_field='id',
    exclude_fields=[],
    include_fields=[],
    extra_fields=[],
    keep_include_fields=True,
    ordering = [],
    show_id = True,
    show_others = True,
    tag_name='data-template',
    tag_id='data-template',
  ):
  model_fields = get_field_names_from_model(django_model)
  inner_header_tr = """
  <th class="data-cell stick-top data-id">#</th>
  """
  # mantain field order
  field_order = list(ordering) # provided order
  for field in include_fields: # include_field order
    if field not in field_order:
      field_order.append(field)
  for field in model_fields: # django model's order
    if field not in field_order:
      field_order.append(field)

  for field in field_order:
    if field is pk_field or not is_includeable(field, include_fields, exclude_fields, keep_include_fields, show_others):
      if show_id and pk_field==field:
        pass
      else:
        continue
    header_name = get_header_name_from_field_name(django_model, field)
    inner_header_tr += f'<th class="data-cell stick-top data-id" title="{field}">{header_name}</th>\n'
    
  
  header_tr = f"""
  <tr class="data-row data-head-row">
  {inner_header_tr}
  </tr>
  """

  table_tag = f"""
  <div class="container">
    <div class="data-wrapper">
      <table class="data-container">
        <thead class="data-head">
          {header_tr}
        </thead>
        <tbody id="data">
            
        </tbody>
      </table>
    </div>
  </div>
  """
  return table_tag
