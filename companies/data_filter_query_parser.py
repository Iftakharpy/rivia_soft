from django.db.models import Q
from django.db.models.fields import (
    DateField, DateTimeField, IntegerField, FloatField, BooleanField, UUIDField
)
from django.db.models.fields.related import ForeignKey
from django.core.exceptions import FieldDoesNotExist
from django.utils.dateparse import parse_datetime
from uuid import UUID
import re
from functools import reduce
import operator


def parse_data_filter_queryset(model, data_filter_query):
    """
    Parses a data filter query string with AND/OR logic and returns a Q object.

    Args:
        model: The Django model class to be filtered.
        data_filter_query: A string representing the filter query.
            - Supports quoted ("string") and unquoted (number, boolean) values.
            - Format: '>field__lookup="value" and field2=value or field3="value"'
            - 'AND' has precedence over 'OR'.

    Returns:
        A Q object representing the parsed filters.
    """
    if not data_filter_query:
        return Q()

    if data_filter_query.startswith('>'):
        data_filter_query = data_filter_query[1:].strip()

    # This regex captures:
    # 1. The key (field name and optional lookup)
    # 2. The operator (>, <, =, !=, etc.)
    # 3. A value in double quotes OR an unquoted value
    pattern = re.compile(r'([\w__]+)\s*([<>]=?|==|!=|=)\s*(?:"([^"]*)"|([^\s]+))')
    
    or_queries = []

    for or_group in data_filter_query.split(' or '):
        or_group = or_group.strip()
        if not or_group:
            continue

        and_queries = []
        for condition in or_group.split(' and '):
            condition = condition.strip()
            if not condition:
                continue

            match = pattern.match(condition)
            if not match:
                continue

            key, op, quoted_value, unquoted_value = match.groups()
            value_str = quoted_value if quoted_value is not None else unquoted_value
            
            # Normalize '=' to '==' for internal lookup mapping
            if op == '=':
                op = '=='

            lookup_map = {'>': 'gt', '>=': 'gte', '<': 'lt', '<=': 'lte', '==': 'exact', '!=': 'exact'}
            negate = (op == '!=')
            lookup = lookup_map.get(op)
            filter_key = key if '__' in key else f"{key}__{lookup}"

            base_field_name = key.split('__')[0]
            value = value_str
            try:
                field = model._meta.get_field(base_field_name)
                
                # If filtering directly on a ForeignKey (e.g., assigned_to=5),
                # cast the value to the type of the related model's primary key.
                if isinstance(field, ForeignKey) and '__' not in key:
                    pk_field = field.related_model._meta.pk
                    if isinstance(pk_field, IntegerField):
                        value = int(value_str)
                    elif isinstance(pk_field, UUIDField):
                        value = UUID(value_str)
                # Handle other standard field types
                elif isinstance(field, DateTimeField): value = parse_datetime(value_str)
                elif isinstance(field, DateField): value = parse_datetime(value_str).date()
                elif isinstance(field, IntegerField): value = int(value_str)
                elif isinstance(field, FloatField): value = float(value_str)
                elif isinstance(field, BooleanField): value = value_str.lower() in ('true', '1', 'yes')
                elif isinstance(field, UUIDField): value = UUID(value_str)

            except (FieldDoesNotExist, ValueError, TypeError, AttributeError):
                # Fallback to using the raw string value if casting fails
                pass

            q_object = Q(**{filter_key: value})
            if negate:
                and_queries.append(~q_object)
            else:
                and_queries.append(q_object)

        if and_queries:
            or_queries.append(reduce(operator.and_, and_queries))

    if not or_queries:
        return Q()

    return reduce(operator.or_, or_queries)


def parse_data_filter_queryset_2(model, data_filter_query):
    pass