from itertools import chain
from django.db import models
from typing import Any, Type, Mapping


ModelClass = Type[models.Model]


class ChainedQuerysetsWithCount:
    def __init__(self, *querysets):
        self.chained_queryset = chain(*querysets)
        self.total_count = sum(map(lambda queryset: queryset.count(), querysets))

    def __iter__(self):
        return self.chained_queryset
    
    def count(self):
        return self.total_count


def model_field_to_form_meta(field: models.Field, load_fk_options=False) -> dict[str, Any]:
    """
    Maps a Django model field to its HTML and Python metadata.
    Includes options for fields with choices or foreign keys.
    
    Args:
        field (Field): A Django model field instance.
        
    Returns:
        dict: A dictionary containing the field name, Django field type, HTML tag, 
              HTML input type, Python type, and options.
    """
    match field:
        case models.TextField:
            html_tag = "textarea"
            html_tag_type = None
            python_type = "str"
        case models.CharField:
            html_tag = "input"
            html_tag_type = "text"
            python_type = "str"
        case models.EmailField:
            html_tag = "input"
            html_tag_type = "email"
            python_type = "str"
        case models.URLField:
            html_tag = "input"
            html_tag_type = "url"
            python_type = "str"
        case models.BooleanField:
            html_tag = "input"
            html_tag_type = "checkbox"
            python_type = "bool"
        case models.DateField:
            html_tag = "input"
            html_tag_type = "date"
            python_type = "datetime.date"
        case models.DateTimeField:
            html_tag = "input"
            html_tag_type = "datetime-local"
            python_type = "datetime.datetime"
        case models.TimeField:
            html_tag = "input"
            html_tag_type = "time"
            python_type = "datetime.time"
        case models.DecimalField:
            html_tag = "input"
            html_tag_type = "number"
            python_type = "float"
        case models.IntegerField:
            html_tag = "input"
            html_tag_type = "number"
            python_type = "int"
        case models.SlugField:
            html_tag = "input"
            html_tag_type = "text"
            python_type = "str"
        case models.ForeignKey:
            html_tag = "select"
            html_tag_type = None
            python_type = "int"  # Typically refers to the related model's primary key
        case models.field:
            html_tag = "input"
            html_tag_type = "text"
            python_type = "str"


    # Check if the field has choices
    if field.choices:
        html_tag = "select"
        html_tag_type = None  # Select tag doesn't use a "type" attribute
        options = [{"value": choice[0], "display": choice[1]} for choice in field.choices]
    else:
        options = None
    
    if load_fk_options and isinstance(field, models.ForeignKey):
        related_model = field.related_model
        options = [
            {"value": obj.pk, "display": str(obj)} for obj in related_model.objects.all()
        ]

    # Return metadata
    return {
        # "python_type": python_type,
        # "django_field_type": field.__class__.__name__,
        "name": field.name,
        "label": field.verbose_name,
        "html_tag": html_tag,
        "html_tag_type": html_tag_type,
        "options": options,
    }



def is_includeable(field, include_fields=[], exclude_fields=[], keep_include_fields=True, show_others=False):
  # skip if exclude_fields contains the field and keep_include_fields is False
  if field in exclude_fields and keep_include_fields is False:
    return False
  # skip if neither include_fields nor exclude_fields contains the field and show others is False
  if (field not in include_fields and field not in exclude_fields) and show_others is False:
    return False
  return True


def get_nested_attr(obj: object, attr: str, default=None, attr_split_on='.'):
    """Filter tag to get python object's attributes.
    Supportes nested attributes separated by '.'.
    If attribute doesn't exists returns None as default.
    """
    attrs = attr.split(attr_split_on)
    value = obj
    for attr in attrs:
        if hasattr(value, 'get'):
            value = value.get(attr, default) # type: ignore
        else:
            value = getattr(value, attr, default)
    return value

def get_field_names_from_model(django_model: ModelClass):
  field_names = []
  for field in django_model._meta.fields:
    field_names.append(field.name)
  return field_names

def get_header_name_from_field_name(django_model, field_name:str):
  try:
    return str(django_model._meta.get_field(field_name).verbose_name)
  except:
    try:
      return str(django_model._meta.get_field(field_name).name)
    except:
      return ' '.join(map(lambda word: word.capitalize(), field_name.split('_')))


def get_field_names_with_label(
      django_model: ModelClass,
      exclude_fields_containing_name:list[str]=["password"]
    ) -> list[dict[str, str]]:
  """
  Generates a list of dictionaries, each containing the 'name' and 
  'label' (verbose name) for all fields on the model, including nested 
  attributes for Foreign Keys.
  """
  fields_with_labels: list[dict[str, Any]] = []

  for field in django_model._meta.fields:
    field_name = field.name
    field_label = get_header_name_from_field_name(django_model, field_name)
    
    should_we_skip_it = False
    for exclude_name in exclude_fields_containing_name:
       if exclude_name in field_name:
          should_we_skip_it = True
          break
    if should_we_skip_it:
       continue

    fields_with_labels.append({
        'name': field_name,
        'label': field_label,
        'is_nested': False,
    })
    
    # Check if the field is a ForeignKey to look for nested attributes
    if isinstance(field, models.ForeignKey):
      # Get the related model class
      related_model: ModelClass = get_nested_attr(field, 'related_model')
      
      if related_model:
        # Iterate over the fields of the related model
        for related_field in related_model._meta.fields:
          # Construct the nested field name (e.g., 'user__first_name')
          nested_field_name = f'{field_name}.{related_field.name}'
          
          should_we_skip_it = False
          for exclude_name in exclude_fields_containing_name:
            if exclude_name in nested_field_name:
              should_we_skip_it = True
              break
          if should_we_skip_it:
            continue
        
          # Construct the nested label (e.g., 'User First Name')
          # We use the verbose name of the related model's field
          nested_label = f"{field_label} {get_header_name_from_field_name(related_model, related_field.name)}"
          fields_with_labels.append({
              'name': nested_field_name,
              'label': nested_label.strip(),
              'is_nested': True,
              'foreign_key_model': related_model.__name__
          })
  return fields_with_labels



def group_fields_by_uniqueness(
    all_model_fields: dict[str, list[dict[str, Any]]]
) -> dict[str, list[dict[str, Any]]]:
    """
    Groups fields from an arbitrary number of model lists into common and unique categories.

    Common fields are those present in ALL models.
    Unique fields are those present in ONLY ONE model.

    Args:
        all_model_fields: A dictionary where keys are model names (str) and values 
                          are lists of field dictionaries for that model.

    Returns:
        A dictionary containing the 'common_fields' list, and lists prefixed by 
        'unique_[model_name]_fields' for each unique set.
    """
    
    total_models = len(all_model_fields)
    if total_models<=1:
       return all_model_fields
    
    # Structure 1: Map field name to the set of models that contain it
    field_sources: dict[str, set[str]] = {}
    
    # Structure 2: Store the original field dictionary for later retrieval
    field_definitions: dict[str, dict[str, Any]] = {}

    for model_name, field_list in all_model_fields.items():
        for field_dict in field_list:
            name = field_dict['name']
            
            # Track the source model(s) for the field name
            if name not in field_sources:
                field_sources[name] = set()
            field_sources[name].add(model_name)
            
            # Store the field dictionary itself. We use the last encountered dict
            # if the field is common (this is an acceptable simplification).
            field_definitions[name] = field_dict 

    # 3. Initialize results and unique field lists for each model
    results: dict[str, list[dict[str, Any]]] = {
        "common_fields": []
    }
    
    for model_name in all_model_fields.keys():
        results[f"unique_{model_name.lower()}_fields"] = []

    # 4. Process all field names based on the number of sources
    for name, sources in field_sources.items():
        field_dict = field_definitions[name]
        num_sources = len(sources)

        if num_sources == total_models:
            # Field is Common to ALL models
            results["common_fields"].append(field_dict)
            
        elif num_sources == 1:
            # Field is Unique to ONE model
            unique_model_name = list(sources)[0]
            key = f"unique_{unique_model_name.lower()}_fields"
            results[key].append(field_dict)
            
        # Note: Fields present in a subset (1 < num_sources < total_models) are ignored 
        # in this implementation, as they are neither truly 'common' nor 'unique'.
        
    return results
