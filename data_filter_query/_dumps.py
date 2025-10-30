import re
from enum import Enum
from django.db.models import Model


# I - Ignore case
# M - Multi-line
# U - Unicode matching
# S - Dot(.) matches all
RE_FLAGS = re.I|re.M|re.U|re.S


class TokenType(Enum):
    """The token types and their regex patterns, these patterns are intend to parse tokens"""
    NONE = re.compile(fr"(?:None|null)", RE_FLAGS)

    FALSE = re.compile(fr"(?:False|F)", RE_FLAGS)
    TRUE = re.compile(fr"(?:True|T)", RE_FLAGS)
    BOOLEAN = re.compile(fr"(?:{FALSE.pattern}|{TRUE.pattern})", RE_FLAGS)

    SIGN = re.compile(fr"(?:[-+])", RE_FLAGS)
    DIGITS = re.compile(fr"(?:\d+)", RE_FLAGS)
    INT = re.compile(fr"{SIGN.pattern}?{DIGITS.pattern}", RE_FLAGS)
    FLOAT = re.compile(fr"{INT.pattern}\.{DIGITS.pattern}", RE_FLAGS)
    
    EMPTY_STRING = re.compile(fr"(?:\"(?:\\\"|.)*?\")", RE_FLAGS)
    NON_EMPTY_STRING = re.compile(fr" (?:\"(?:\\\"|.)+?\")", RE_FLAGS)
    WHITESPACE = re.compile(fr"(?:\s|\r|\n|\t)", RE_FLAGS)

    LIST_ITEM_SEPARATOR = re.compile(fr"(?:{WHITESPACE.pattern}*,{WHITESPACE.pattern}*)", RE_FLAGS)
    # This is simpler then the one below
    LIST = re.compile(fr"\[.+?\]", RE_FLAGS)
    # Zero or more string, float, int, boolean and the separator(,) is optional spaces are optional too
    # LIST = re.compile(fr"\[\s*(?:(?:(?P<none>{NONE.pattern})|(?P<boolean>{BOOLEAN.pattern})|(?P<int>{INT.pattern})|(?P<float>{FLOAT.pattern})|(?P<string>{EMPTY_STRING.pattern}))(?P<separator>{LIST_ITEM_SEPARATOR.pattern})?)*\]", RE_FLAGS)

    LOGICAL_AND = re.compile(fr"(?:&|and)", RE_FLAGS)
    LOGICAL_OR = re.compile(fr"(?:\||or)", RE_FLAGS)
    OPEN_PAREN = re.compile(fr"\(", RE_FLAGS)
    CLOSE_PAREN = re.compile(fr"\)", RE_FLAGS)

    LOOKUP_OPERATOR = re.compile(fr"(?:==|=|>=|>|<=|<|[\w_]+)", RE_FLAGS)
    FIELD_NAME = re.compile(fr"(?:[\w_]+)", RE_FLAGS)
    FIELD_VALUE = re.compile(fr"(?:{NONE.pattern}|{BOOLEAN.pattern}|{INT.pattern}|{FLOAT.pattern}|{EMPTY_STRING}|{LIST})", RE_FLAGS)






def generate_query_schema(model: type[Model], prefix="", visited_models=None, current_depth=-1, max_depth=1):
    """
    Generates a schema of filterable fields and their supported lookups for a model.
    Handles nested relations recursively and prevents infinite loops.
    """
    if visited_models is None:
        visited_models = set()

    if model in visited_models:
        return {} # Prevent infinite recursion

    visited_models.add(model)
    
    schema = {}
    if current_depth>=max_depth:
        return schema
    
    for field in model._meta.get_fields():
        if field.is_relation:
            # For relations, allow filtering by related fields
            if field.related_model:
                nested_prefix = f"{prefix}{field.name}__"
                nested_schema = generate_query_schema(
                    model=field.related_model, 
                    prefix=nested_prefix,
                    visited_models=visited_models.copy(), # Pass a copy
                    current_depth=current_depth+1,
                    max_depth=max_depth
                )
                schema.update(nested_schema)
        else:
            # For regular fields
            field_name = f"{prefix}{field.name}"
            schema[field_name] = {
                "type": field.get_internal_type(),
                "lookups": set(field.get_lookups().keys()),
                "help_text": str(field.help_text) or f"Field of type {field.get_internal_type()}"
            }
    return schema




