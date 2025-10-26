from django import template
from django.utils.safestring import mark_safe
from django.utils.encoding import is_protected_type
from pprint import pp
import json


register = template.Library()


@register.filter(name='addstr')
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    concatinated = str(arg1) + str(arg2)
    return mark_safe(concatinated)


@register.filter(name='convert_to_JSON')
def convert_obj_to_JSON(obj, indent_spaces=None):
    """
    Converts a Python object to a JSON string.
    
    Accepts an optional integer for indentation (e.g., |convert_to_JSON:4).
    """
    
    # --- IMPORTANT FIX for __proxy__ error ---
    # Ensure any lazy/proxy objects are evaluated to a string before serialization.
    # This prevents the TypeError: __proxy__ object can't be serialized
    if is_protected_type(obj):
        obj = str(obj)
    # --- End of Fix ---

    try:
        # If indent_spaces is provided (e.g., '4'), convert it to an integer.
        # If it's None, json.dumps uses no indentation.
        indent_val = int(indent_spaces) if indent_spaces is not None else None
        
        return json.dumps(obj, indent=indent_val)
    except Exception as e:
        # Handle cases where the object is still not serializable or indent_spaces is invalid
        print(f"Error in convert_to_JSON filter: {e}")
        return json.dumps(str(obj)) # Fallback to a string representation


@register.filter('dir')
def get_dir(obj):
    attrs = {}
    for attr in dir(obj):
        attrs[attr] = str(getattr(obj, attr, None))
    response = json.dumps(attrs, indent=4)
    return response


@register.filter(name='get_attr')
def get_nested_attr(obj, attr, default=None, attr_split_on='.'):
    """Filter tag to get python object's attributes.
    Supportes nested attributes separated by '.'.
    If attribute doesn't exists returns None as default.
    """
    attrs = attr.split(attr_split_on)
    value = obj
    for attr in attrs:
        value = getattr(value, attr, default)
    return value


@register.filter(name='get_field')
def get_field(form, field_name):
    return form[field_name]


@register.filter
def startswith(value, arg):
    """Checks if a string starts with a given substring."""
    return value.startswith(arg)
@register.filter
def endswith(value, arg):
    """Checks if a string starts with a given substring."""
    return value.endswith(arg)
