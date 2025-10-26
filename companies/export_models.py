from typing import Type
from django.db.models.fields.related import ForeignKey
from django.db.models import Model
from .utils import is_includeable, get_nested_attr, get_header_name_from_field_name, get_field_names_from_model
import csv
from pprint import pp


def export_to_csv(
    django_model: Model,
    write_to,
    exclude_fields = [],
    include_fields = [],
    ordering = [],
    keep_include_fields = True,
    show_others = True,
    fk_fields = {
      # 'fk_field_name_in_model': ['referenced_model_field_names']
    },
    write_header_row=True,
    records=None,
    column_name_split_on="__"
    ):
  model_fields = get_field_names_from_model(django_model)
  writer = csv.writer(write_to)

  # mantain field order
  field_order = list(ordering) # provided order
  for field in include_fields: # include_field order
    if field not in field_order:
      field_order.append(field)
  for field in model_fields: # django model's order
    if field not in field_order:
      field_order.append(field)
  
  # prepare csv file header
  header = [] # header row
  columns = []
  for field in field_order:
    # skip if field is pk_field
    if not is_includeable(field, include_fields, exclude_fields, keep_include_fields, show_others):
      continue
    
    # handle foreign key field
    if field in fk_fields:
      nested_model:Model = get_nested_attr(django_model, f'{field}.field.related_model', attr_split_on=".")
      nested_fields = fk_fields[field]
      
      if nested_fields == "all":
        django_fields = nested_model._meta.get_fields()
        nested_fields = []
        for dj_filed in django_fields:
          nested_fields.append(dj_filed.name)

      for nested_field in nested_fields:
        nested_header_name = get_header_name_from_field_name(nested_model, nested_field)
        nested_column_name = f'{field}__{nested_field}'
        header.append(f"{nested_model.__name__} - {nested_header_name}")
        columns.append(nested_column_name)
      continue

    header_name = get_header_name_from_field_name(django_model, field)
    column_name = field
    header.append(header_name)
    columns.append(column_name)

  # write header row
  if write_header_row:
    writer.writerow(header)
  del(header)

  # write data rows
  if records is None:
    records = django_model.objects.all()
  for record in records:
    row = []
    for column in columns:
      value = get_nested_attr(record, column, attr_split_on=column_name_split_on)
      row.append(value)
    # write record
    writer.writerow(row)
  del(records)
  del(writer)
