import re
import math
from ast import literal_eval
from enum import Enum, auto
from typing import Callable, Any
from dataclasses import dataclass
from collections import deque
from django.db.models import Model, Q, QuerySet
from django.db.models.fields import Field
from django.db.models.lookups import Lookup
from django.core.exceptions import FieldDoesNotExist, FieldError, ValidationError

# from pprint import pp
# from debug_funcs import log_all_frame_locals, log_stack
# from .debug_funcs import log_all_frame_locals, log_stack


FIELD_LOOKUP_SPEC = f"""[field_name lookup_expr value]"""
SPACE_CHARS = re.compile(r"^\s$")
ALLOWED_CHARS_IN_FIELD_NAME = re.compile(r"[a-zA-Z_0-9]")
ALLOWED_CHARS_IN_LOOKUP = re.compile(r"[a-zA-Z<>!^$*~=]| ")
ALLOWED_CHARS_IN_VALUE = re.compile(r"(.|\s)")
ALLOWED_OPERATORS_REGEX = re.compile(r"^(?:(?:[<>!^$*~=]{1,})|(?:(?:(?:not|is) |[!])?\w+)) ?$", re.MULTILINE|re.IGNORECASE)
ALLOWED_LOGICAL_OPERATOR_REGEX = re.compile(r"^(?:or|[|]{1,2})|(?:and|[&]{1,2})$")
LOGICAL_OPERATOR_PRECEDENCE = {
	'and': 2, # higher
	'or': 1 #  lower
}
GROUP_OPEN2CLOSE_CHARS = {
	"(": ")",
}
GROUP_CLOSE2OPEN_CHARS = {v:k for k,v in GROUP_OPEN2CLOSE_CHARS.items()}
STRING_OPEN2CLOSE_BOUNDARY_CHARS = {
		"'": "'",
		'"': '"',
		"[": "]",
		"{": "}",
	}
STRING_CLOSE2OPEN_BOUNDARY_CHARS = {v:k for k,v in STRING_OPEN2CLOSE_BOUNDARY_CHARS.items()}
VALID_FIELD_LOOKUPS = {
		"=", "==", "is", "eq", # equals
		"!=", "eq", # not equals
		"<", ">", "<=", ">=", # lt, gt, lte, gte
		"^=", "$=", "*=", "~=", # starts, ends, contains

		# --- General / Most Common Lookups ---
		'exact',        # Exact match. Default if no lookup is provided. Ex: .filter(title__exact="Hello")
		'iexact',       # Case-insensitive exact match. Ex: .filter(title__iexact="hello")
		'contains',     # Case-sensitive containment. Ex (Text): .filter(title__contains="World") | Ex (JSON): .filter(meta__contains={'id': 1})
		'icontains',    # Case-insensitive containment (for text). Ex: .filter(title__icontains="world")
		'gt',           # Greater than. Ex: .filter(views__gt=100)
		'gte',          # Greater than or equal to. Ex: .filter(views__gte=100)
		'lt',           # Less than. Ex: .filter(views__lt=50)
		'lte',          # Less than or equal to. Ex: .filter(views__lte=50)
		'in',           # In a given list, tuple, or queryset. Ex: .filter(pk__in=[1, 3, 5])
		'isnull',       # Checks if the value is NULL. Expects a boolean. Ex: .filter(content__isnull=True)

		# --- String-Specific Lookups ---
		'startswith',   # Case-sensitive starts-with. Ex: .filter(title__startswith="How")
		'istartswith',  # Case-insensitive starts-with. Ex: .filter(title__istartswith="how")
		'endswith',     # Case-sensitive ends-with. Ex: .filter(email__endswith="@example.com")
		'iendswith',    # Case-insensitive ends-with. Ex: .filter(email__iendswith="@example.com")
		'regex',        # Case-sensitive regular expression match. Ex: .filter(title__regex=r'^(An?|The) ')
		'iregex',       # Case-insensitive regular expression match. Ex: .filter(title__iregex=r'^(an?|the) ')
		'soundex',      # Matches based on the Soundex algorithm (database-specific). Ex: .filter(last_name__soundex='Jansen')

		# --- Date and DateTime Lookups ---
		'date',         # Casts a DateTimeField to a date for matching. Ex: .filter(published_at__date=date(2024, 1, 15))
		'year',         # Extracts the year as an integer. Ex: .filter(published_at__year=2023)
		'month',        # Extracts the month as an integer (1-12). Ex: .filter(published_at__month=12)
		'day',          # Extracts the day as an integer (1-31). Ex: .filter(published_at__day=25)
		'week',         # Extracts the ISO week number as an integer (1-53). Ex: .filter(published_at__week=3)
		'week_day',     # Extracts the day of the week (e.g., 1=Sun, 2=Mon). Ex: .filter(published_at__week_day=2)
		'quarter',      # Extracts the quarter of the year as an integer (1-4). Ex: .filter(published_at__quarter=1)
		'time',         # Extracts the time from a DateTimeField for matching. Ex: .filter(start_time__time=time(14, 30))
		'hour',         # Extracts the hour as an integer (0-23). Ex: .filter(start_time__hour=15)
		'minute',       # Extracts the minute as an integer (0-59). Ex: .filter(start_time__minute=30)
		'second',       # Extracts the second as an integer (0-59). Ex: .filter(start_time__second=0)

		# --- Range Lookup ---
		'range',        # Checks if a value is between two others (inclusive). Ex: .filter(views__range=(100, 500))

		# --- PostgreSQL-Specific Lookups ---
		'contained_by', # (Array) Is a subset of the given list. (JSON) Is a subset of the given JSON. Ex: .filter(tags__contained_by=['py', 'web'])
		'overlap',      # (Array) Has any elements in common with the given list. Ex: .filter(tags__overlap=['news', 'tech'])
		'len',          # (Array) Allows filtering on the length of the array. Ex: .filter(tags__len__gt=3)
		'has_key',      # (JSON/HStore) Contains a specific top-level key. Ex: .filter(meta__has_key='tags')
		'has_keys',     # (JSON/HStore) Contains all of the specified top-level keys. Ex: .filter(meta__has_keys=['user', 'tags'])
		'has_any_keys', # (JSON/HStore) Contains any of the specified top-level keys. Ex: .filter(meta__has_any_keys=['editor', 'moderator'])
	}
FIELD_LOOKUP_REMAPS = {
	# NOTE: in the value of the dict use '!' for negations
	# for example: {key: value} -> {"is not": "!exact"}
	
	# equals
	"=": "exact",
	"==": "exact", 
	"eq": "exact",
	"is": "exact",
	"not": "!exact",
	"is not": "!exact",

	# # Not necessary should work because of field_value_literal_eval
	# "is null": "isnull",
	# "not null": "!isnull",

	"not in": "!in",
	
	# lt, gt, lte, gte
	"<": "lt",
	">": "gt",
	"<=": "lte",
	">=": "gte",
	
	# starts, ends, contains
	"^=": "istartswith", 
	"$=": "iendswith",
	"*=": "icontains",
	"~=": "iregex",
}



@dataclass
class ParserControl:
	"""
	A data class to manage the state of a process, like parsing.

	Attributes:
		should_continue (bool): Flag to indicate if the process should continue to the next iteration.
		should_consume (bool): Flag to indicate if the current item should be consumed or processed.
	"""
	should_continue: bool
	should_consume: bool
	def __iter__(self):
		# Yield to support unpacking
		yield self.should_continue
		yield self.should_consume

CharPredicate = Callable[[int, int, str], ParserControl]
def __consume_chars(
	data_filter_query: str, 
	start_idx: int, 
	end_idx: int, 
	allowed_chars_regex: re.Pattern,
	callback_on_chars: set[str]|re.Pattern|None = None,
	callback_function: CharPredicate|None = None,
	stop_on_consumed_substr__regex_match: re.Pattern|None=None,
	stop_on_consumed_substr__regex_no_match: re.Pattern|None=None,
) -> tuple[int, bool, str]:
	"""
	Consumes characters from `data_filter_query` in range [start_idx, end_idx]. 
	Stops on the first character that fails either the callback check or the regex match.

	Returns:
		tuple[int, bool, str]: (idx after consumption, success status, consumed string or failure message).

	Args:
		data_filter_query (str): Input string.
		start_idx (int): Start index (inclusive).
		end_idx (int): End index (inclusive). Use -1 for end of string.
		allowed_chars_regex (re.Pattern): Compiled regex for a single allowed character.
		callback_on_chars (set[str]): A set of specific characters that, when encountered,
									  will trigger a call to `callback_function`. Defaults to an empty set.
		callback_function (CharPredicate): A function with the signature **(curr_idx:int, consumed_len:int, char:str) -> tuple[bool, bool]** called. Meaning of return value [should_continue, should_consume]
										   when a character in `callback_on_chars` is found. If it returns 
										   **False**, consumption immediately stops.
		stop_on_consumed_substr__regex_match (re.Pattern|None): returns with success when consumed string matches the regex.
		stop_on_consumed_substr__regex_no_match: re.Pattern|None: returns with success when consumed string matches the regex.
	"""
	if end_idx==-1:
		end_idx = len(data_filter_query)-1
	elif end_idx>=len(data_filter_query):
		msg = f"""end_idx={end_idx} >= len(data_filter_query)={len(data_filter_query)}"""
		return start_idx, False, msg
	if start_idx>end_idx:
		msg = f"""start_idx={start_idx} > end_idx={end_idx}"""
		return start_idx, False, msg
	
	
	consumed_string = ""
	idx = start_idx
	while (idx<=end_idx):
		ch = data_filter_query[idx]
		if callback_on_chars:
			should_I_callback = ((type(callback_on_chars)==set and ch in callback_on_chars) or 
						(type(callback_on_chars)==re.Pattern and callback_on_chars.fullmatch(ch)))
			if should_I_callback and callback_function:
				should_continue, should_consume = callback_function(idx, idx-start_idx, ch)
				if should_consume:
					consumed_string += ch
					idx+=1
				if not should_continue:
					return idx, True, consumed_string
				
				if not should_consume:
					idx+=1
				continue
		
		# check for match with regex pattern
		if not allowed_chars_regex.fullmatch(ch):
			break

		consumed_string += ch
		idx += 1

		if stop_on_consumed_substr__regex_match and (stop_on_consumed_substr__regex_match.fullmatch(consumed_string)):
			return idx+1, True, consumed_string
		if stop_on_consumed_substr__regex_no_match and not(stop_on_consumed_substr__regex_no_match.fullmatch(consumed_string)):
			return idx-1, True, consumed_string[:-1]
			
	if len(consumed_string)==0:
		msg = """Couldn't consume any valid chars."""
		return idx, False, msg
	return idx, True, consumed_string
def __consume_sequence_of_chars(
		data_filter_query: str, 
		start_idx: int,
		char_sequence: str,
		is_case_insensitive:bool = False
	) -> tuple[int, bool]:
	end_idx = len(data_filter_query)-1
	idx = start_idx
	while idx<=end_idx and (idx-start_idx)<len(char_sequence):
		q_ch = data_filter_query[idx]
		s_ch = char_sequence[idx-start_idx]
		if is_case_insensitive:
			q_ch = q_ch.lower()
			s_ch = s_ch.lower()
		if q_ch!=s_ch:
			break
		idx+=1

	if (idx-start_idx)==len(char_sequence):
		return idx, True
	return idx, False



def get_nested_attr(obj: object, attr: str, default=None, attr_split_on='__'):
	"""Filter tag to get python object's attributes.
	Supports nested attributes separated by '__'.
	If attribute doesn't exists returns None as default.
	"""
	attrs = attr.split(attr_split_on)
	value = obj
	for attr in attrs:
		value = getattr(value, attr, default)
	return value

def _get_field_from_path(model: type[Model], path: str, default=None, attr_split_on='__') -> Field | None:
	"""
	Traverses a model relationship path (e.g., 'author__name') and returns the final field.
	Returns None if the path is invalid.
	"""
	current_model = model
	field = None
	parts = path.split(attr_split_on)
	
	for i, part in enumerate(parts):
		try:
			field = current_model._meta.get_field(part)
			# If this is a relational field and not the last part of the path,
			# move to the related model for the next iteration.
			if hasattr(field, 'related_model') and field.related_model and i < len(parts) - 1:
				current_model = field.related_model
		except FieldDoesNotExist:
			return default
	return field

def field__from__field_name(model: type[Model]|None, field_name: str) -> Field|None:
	if model is None:
		return None
	field = _get_field_from_path(model, field_name, None, attr_split_on="__")
	if isinstance(field, Field):
		return field
	return None
def is_valid__field_name(model: type[Model]|None, field_name: str) -> bool:
	if model is None:
		return True
	return None is not field__from__field_name(model, field_name)
def __consume__field_name(
		model: type[Model]|None,
		data_filter_query: str,
		start_idx: int=0,
		end_idx: int=-1) -> tuple[int, bool, str]:
	##############################################################
	### field_name: try to consume 
	field_name = ""
	# consume possible empty spaces before field_name
	idx, _is_success, _error_msg__or__data = __consume_chars(data_filter_query, start_idx, end_idx, SPACE_CHARS)
	# check beginning with char
	if not (data_filter_query[idx]=="_" or data_filter_query[idx].isalpha()):
		msg = f"""@idx={idx} Invalid field_name. Field name can only start with (a-z, A-Z or _) chars."""
		return idx, False, msg
	idx, is_success, error_msg__or__data = __consume_chars(data_filter_query, idx, end_idx, ALLOWED_CHARS_IN_FIELD_NAME)
	
	if is_success: field_name = error_msg__or__data
	else: return idx, False, error_msg__or__data
	# field_name: consumed
	if not is_valid__field_name(model, field_name):
		msg = f"""@idx={idx} Invalid field_name='{field_name}'."""
		return idx, False, msg
	return idx, True, field_name
	### field_name: consumed successfully
	##############################################################


def field_lookup__resolve(field_lookup_expression: str) -> str:
	lookup_remap = FIELD_LOOKUP_REMAPS.get(field_lookup_expression)
	field_lookup_expression = lookup_remap if lookup_remap is not None else field_lookup_expression
	return field_lookup_expression
def field_lookup__from__field_lookup_expression(model: type[Model]|None, field_name: str, field_lookup_expression: str) -> Lookup|None:
	if model is None:
		return None
	field: Field|None = field_name if model is None else field__from__field_name(model, field_name)
	field_lookup = field_lookup__resolve(field_lookup_expression).removeprefix("not ").removeprefix("!")
	lookup = None
	if field and hasattr(field, 'get_lookup'):
		lookup = field.get_lookup(field_lookup)
	return lookup
def is_valid__field_lookup_expression(model: type[Model]|None, field_name: str, field_lookup_expression: str) -> bool:
	field_lookup = field_lookup__resolve(field_lookup_expression).removeprefix("not ").removeprefix("!")
	if model is None:
		return field_lookup in VALID_FIELD_LOOKUPS
	lookup = field_lookup__from__field_lookup_expression(model, field_name, field_lookup)
	return None is not lookup
def __consume__field_lookup_operator(
		model: type[Model]|None,
		data_filter_query: str,
		start_idx: int=0,
		end_idx: int=-1,
		field_name:str|None = None,
		) -> tuple[int, bool, str]:
	##############################################################
	### field_lookup_operator: try to consume
	field_lookup_expression = ""

	idx, _is_success, _error_msg__or__data = __consume_chars(
		data_filter_query, start_idx, end_idx, SPACE_CHARS,
		)
	
	new_idx, is_success, error_msg__or__data = __consume_chars(
		data_filter_query, idx, end_idx, ALLOWED_CHARS_IN_LOOKUP,
		stop_on_consumed_substr__regex_no_match=ALLOWED_OPERATORS_REGEX,
		)
	if is_success:
		field_lookup_expression = error_msg__or__data.lower().strip()
		first_word = field_lookup_expression.split(' ')[0]
		if field_lookup_expression in VALID_FIELD_LOOKUPS or field_lookup_expression in FIELD_LOOKUP_REMAPS:
			idx = new_idx
		elif first_word in VALID_FIELD_LOOKUPS:
			field_lookup_expression = first_word
			idx += len(first_word)
		elif first_word in FIELD_LOOKUP_REMAPS:
			field_lookup_expression = first_word
			idx += len(first_word)
		else:
			idx = new_idx
	else:
		idx = new_idx
		msg = f"""@idx={idx} Expected field_lookup_operator -> {error_msg__or__data}"""
		return idx, False, msg
	field_lookup_expression = field_lookup_expression.strip()
	# field_lookup_operator: consumed

	is_negated_lookup = field_lookup_expression.startswith("!") or field_lookup_expression.startswith("not ")
	lookup_part = field_lookup_expression.removeprefix("not ").removeprefix("!")
	lookup_part = FIELD_LOOKUP_REMAPS.get(lookup_part, lookup_part)
	
	if field_name and not is_valid__field_lookup_expression(model, field_name, field_lookup_expression):
		msg = f"""@idx={idx} Invalid field_lookup_expression='{field_lookup_expression}'"""
		return idx, False, msg
	
	if is_negated_lookup:
		field_lookup_expression = f"!{lookup_part}"
	elif field_lookup_expression in FIELD_LOOKUP_REMAPS:
		field_lookup_expression = lookup_part
	return idx, True, field_lookup_expression
	### field_lookup_operator: consumed successfully
	##############################################################

FIELD_VALUE_LITERAL_REMAPPING = {
	'y': True,
	'yes': True,
	'yeah': True,
	'true': True,
	'n': False,
	'no': False,
	'nah': False,
	'false': False,
	'na': None,
	'n/a': None,
	'null': None,
	'none': None,
}
def literal_eval__field_lookup_value(field_lookup_value: str) -> Any:
	try:
		# literal_eval is SAFE and only parses basic Python types. It cannot execute code.
		field_lookup_value = literal_eval(field_lookup_value)
		return field_lookup_value
	except (ValueError, SyntaxError, MemoryError, TypeError):
		# If literal_eval fails, it's an unquoted string.
		# Example: `status = active` -> raw_field_lookup_value is 'active'
		# literal_eval('active') fails, so we just use the string 'active'.
		# The final_value already holds the raw string, so we just pass.
		pass
	val = FIELD_VALUE_LITERAL_REMAPPING.get(field_lookup_value.lower(), math.inf)
	is_remapped_value_resolved = not (isinstance(val, float) and math.isinf(val))
	if is_remapped_value_resolved:
		return val
	return field_lookup_value
def is_valid__field_lookup_value(model: type[Model]|None, field_name: str, field_lookup_expression: str, field_lookup_value: str) -> bool:
	if model is None:
		return True
	field = field__from__field_name(model, field_name)
	lookup = field_lookup__from__field_lookup_expression(model, field_name, field_lookup_expression)

	return True
def __consume__field_lookup_value(
		model: type[Model]|None,
		data_filter_query: str,
		start_idx: int = 0,
		end_idx: int = -1,
		field_name:str|None = None,
		field_lookup_expression:str|None = None,
		) -> tuple[int, bool, str]:
	##############################################################
	### field_lookup_value: try to consume
	field_lookup_value = ""
	
	idx, _is_success, error_msg__or__data = __consume_chars(data_filter_query, start_idx, end_idx, SPACE_CHARS)
	if idx>=len(data_filter_query):
		msg = f"""@idx={idx} Expected field_lookup_value -> {error_msg__or__data}"""
		return idx, False, msg
	
	open_boundary_char_stack = deque()
	open_boundary_escape_indexes = set()
	starting_open_ch = data_filter_query[idx]
	does_it_start_with_string_boundary = starting_open_ch in STRING_OPEN2CLOSE_BOUNDARY_CHARS
	starting_close_ch = STRING_OPEN2CLOSE_BOUNDARY_CHARS.get(starting_open_ch) if does_it_start_with_string_boundary else ''
	if does_it_start_with_string_boundary:
		open_boundary_char_stack.append(starting_open_ch)
	def cb_value_consumption(curr_idx, consumed_len, char) -> ParserControl:
		"""Consume until next space char or string_boundary_chars"""
		# if char in GROUP_OPEN2CLOSE_CHARS or char in GROUP_CLOSE2OPEN_CHARS:
		# 	import ipdb; ipdb.set_trace()
		if does_it_start_with_string_boundary:
			if consumed_len<=1:
				return ParserControl(should_continue=True, should_consume=True)
			
			is_open_boundary_char = starting_open_ch==char
			is_close_boundary_char = starting_close_ch==char
			
			is_open_or_close_boundary_char = is_open_boundary_char or is_close_boundary_char
			if (open_boundary_char_stack and is_open_or_close_boundary_char and data_filter_query[curr_idx-1]=='\\' ): # allow escaping escape open or close string token
				open_boundary_escape_indexes.add(consumed_len-1)
				return ParserControl(should_continue=True, should_consume=True)
			
			# Manage the stack for string boundary
			if is_close_boundary_char:
				matching_open_boundary_char = STRING_CLOSE2OPEN_BOUNDARY_CHARS[char]
				if open_boundary_char_stack and matching_open_boundary_char==open_boundary_char_stack[-1]:
					open_boundary_char_stack.pop()
					if len(open_boundary_char_stack)==0: # stack is empty
						return ParserControl(should_continue=False, should_consume=True) # End of the string value.
			elif char==open_boundary_char_stack[-1]:
				open_boundary_char_stack.append(char)
			return ParserControl(should_continue=True, should_consume=True)
		elif char in GROUP_OPEN2CLOSE_CHARS or char in GROUP_CLOSE2OPEN_CHARS: # group close char
			return ParserControl(should_continue=False, should_consume=False)
		else:
			# If not inside a string, stop at the first space.
			return ParserControl(should_continue=not SPACE_CHARS.fullmatch(char), should_consume=False)

	idx, is_success, error_msg__or__data = __consume_chars(
		data_filter_query=data_filter_query,
		start_idx=idx,
		end_idx=end_idx,
		allowed_chars_regex=ALLOWED_CHARS_IN_VALUE,
		callback_on_chars=set(
			list(STRING_OPEN2CLOSE_BOUNDARY_CHARS.keys()) +
			list(STRING_CLOSE2OPEN_BOUNDARY_CHARS.keys()) +
			list(GROUP_OPEN2CLOSE_CHARS.keys()) +
			list(GROUP_CLOSE2OPEN_CHARS)+
			list(" \t\r\n\v\f")
			),
		callback_function=cb_value_consumption,
		)
	if is_success: 
		field_lookup_value = "".join([
			(ch if i not in open_boundary_escape_indexes else '')
				for i, ch in enumerate(error_msg__or__data)
		])
	else: 
		msg = f"""@idx={idx} Expected field_lookup_value -> {error_msg__or__data}"""
		return idx, False, msg
	if field_lookup_value=='':
		msg = f"""@idx={idx} Expected field_lookup_value -> you probably used chars['(', ')'] -> couldn't consume any valid chars"""
		return idx, False, msg
	
	# comment this out for loose string closing requirements
	string_open_boundary_char = field_lookup_value[0]
	if does_it_start_with_string_boundary and len(field_lookup_value)>=2:
		if STRING_OPEN2CLOSE_BOUNDARY_CHARS[string_open_boundary_char] != field_lookup_value[-1]:
			msg = f"""@idx={idx} Expected string_close_boundary_char {STRING_OPEN2CLOSE_BOUNDARY_CHARS[string_open_boundary_char]} -> {error_msg__or__data}"""
			return idx, False, msg
	# field_lookup_value: consumed
	
	field_value = literal_eval__field_lookup_value(field_lookup_value)
	if does_it_start_with_string_boundary and type(field_value)==str and len(field_value)>0 and field_value[0]==string_open_boundary_char and field_value[-1]==string_open_boundary_char:
		field_value = field_value[1:-1]

	if field_name and field_lookup_expression and not is_valid__field_lookup_value(model, field_name, field_lookup_expression, field_lookup_value):
		msg = f"""@idx={idx} Invalid field_lookup_value='{field_lookup_value}'"""
		return idx, False, msg
	
	return idx, True, field_value
	### field_lookup_value: consumed successfully
	##############################################################


@dataclass
class FieldLookupSpec:
	"""Represents a logical operation between two expressions."""
	field_name: str
	field_lookup_expression: str
	field_lookup_value: str
	def __repr__(self) -> str:
		return str(self)
	def __str__(self):
		return f"[{self.field_name} {self.field_lookup_expression} {self.field_lookup_value}]"
	
def __consume_field_spec(model: type[Model]|None, data_filter_query: str, start_idx: int=0, end_idx: int=-1) -> tuple[int, bool, str|FieldLookupSpec]:
	"""Parses a single field specification from a query string.

	A field specification has the format: `field_path lookup_expression value`.

	Examples:
		- `updated_at >= 2020-02-01`
		- `description__contains = 'hello'`
		- `author__name icontains 'smith'`

	Returns:
		tuple[int, bool, str | tuple[str, str, str]]: A tuple containing:
			- int: idx position after parsing.
			- bool: True for success, False for failure.
			- str | tuple[str, str, str]: An error message on failure,
			  or a tuple of (field_path, lookup_expression, value) on success.

	Args:
		data_filter_query (str): The raw query string to parse.
		start_idx (int): [inclusive] The index from which to start parsing.
		end_idx (int): [inclusive] The index at which to stop parsing. Defaults to -1,
			which means parsing to the end of the string.
	"""
	# parse field_name
	idx, is_success, error_msg_or_field_name = __consume__field_name(model, data_filter_query, start_idx, end_idx)
	if not is_success:
		return idx, False, error_msg_or_field_name
	field_name = error_msg_or_field_name

	# parse field_lookup_expression
	idx, is_success, error_msg_or_field_lookup_expression = __consume__field_lookup_operator(model, data_filter_query, idx, end_idx, field_name)
	if not is_success:
		return idx, False, error_msg_or_field_lookup_expression
	field_lookup_expression = error_msg_or_field_lookup_expression

	# parse field_lookup_value
	idx, is_success, error_msg_field_lookup_value = __consume__field_lookup_value(model, data_filter_query, idx, end_idx, field_name, field_lookup_expression)
	if not is_success:
		return idx, False, error_msg_field_lookup_value
	field_lookup_value = error_msg_field_lookup_value

	##############################################################
	# TODO: validate field_lookup_value using field_name and field_lookup_expression
	##############################################################
	return idx, True, FieldLookupSpec(field_name, field_lookup_expression, field_lookup_value)


def __consume__logical_operator(data_filter_query: str, start_idx: int, end_idx: int) -> tuple[int, bool, str]:
	"""
	Consumes a logical operator ('and' or 'or').
	This is a stricter version that ensures the operator is a whole word,
	preventing partial matches like 'and_' from being parsed incorrectly.
	"""
	# 1. Consume any leading whitespace
	idx, _, _ = __consume_chars(data_filter_query, start_idx, end_idx, SPACE_CHARS)
	if idx > end_idx:
		msg = f"""@idx={start_idx} Expected logical_operator{list(LOGICAL_OPERATOR_PRECEDENCE.keys())} -> ran out of chars"""
		return start_idx, False, msg # Not an error, just no match

	original_idx = idx

	# 2. Check for 'and'
	new_idx, is_success = __consume_sequence_of_chars(data_filter_query, idx, "and", is_case_insensitive=True)
	if is_success:
		# Check that 'and' is followed by a space, parenthesis, or end of string
		if new_idx > end_idx or data_filter_query[new_idx].isspace() or data_filter_query[new_idx] in GROUP_OPEN2CLOSE_CHARS:
			# This is a valid 'and'. Consume any trailing space.
			final_idx, _, _ = __consume_chars(data_filter_query, new_idx, end_idx, SPACE_CHARS)
			return final_idx, True, 'and'
		else:
			# It's a malformed operator like 'and_'. Find the end of this "word" for a better error message.
			error_word_end_idx = new_idx
			while error_word_end_idx <= end_idx and ALLOWED_CHARS_IN_FIELD_NAME.fullmatch(data_filter_query[error_word_end_idx]):
				error_word_end_idx += 1
			error_word = data_filter_query[idx:error_word_end_idx]
			msg = f"""@idx={original_idx} Invalid logical_operator '{error_word}'. Did you mean 'and'?"""
			return original_idx, False, msg

	# 3. Check for 'or' with the same logic
	new_idx, is_success = __consume_sequence_of_chars(data_filter_query, idx, "or", is_case_insensitive=True)
	if is_success:
		# Check that 'or' is followed by a space, parenthesis, or end of string
		if new_idx > end_idx or data_filter_query[new_idx].isspace() or data_filter_query[new_idx] in GROUP_OPEN2CLOSE_CHARS:
			# This is a valid 'or'. Consume any trailing space.
			final_idx, _, _ = __consume_chars(data_filter_query, new_idx, end_idx, SPACE_CHARS)
			return final_idx, True, 'or'
		else:
			# It's a malformed operator like 'or_'.
			error_word_end_idx = new_idx
			while error_word_end_idx <= end_idx and ALLOWED_CHARS_IN_FIELD_NAME.fullmatch(data_filter_query[error_word_end_idx]):
				error_word_end_idx += 1
			error_word = data_filter_query[idx:error_word_end_idx]
			msg = f"""@idx={original_idx} Invalid logical_operator '{error_word}'. Did you mean 'or'?"""
			return original_idx, False, msg

	# 4. If neither 'and' nor 'or' was found, return failure
	msg = f"""@idx={start_idx} did not find logical_operator{list(LOGICAL_OPERATOR_PRECEDENCE.keys())}"""
	return start_idx, False, msg



class TokenType(Enum):
	FIELD_SPEC = auto()
	LOGICAL_OP = auto()
	LPAREN = auto()
	RPAREN = auto()

@dataclass
class Token:
	"""Represents a single token from the query string."""
	type: TokenType
	value: Any
	position: int # Store position for better error messages


def _create_q_from_spec(spec: FieldLookupSpec) -> Q:
	"""Converts a FieldLookupSpec into a Django Q object, handling negation."""
	# Build the Django-style lookup string, e.g., 'age__gte'
	lookup = f"{spec.field_name}__{spec.field_lookup_expression}"
	
	# Check for negation in the lookup expression
	is_negated = False
	if spec.field_lookup_expression.startswith(('!', 'not ')):
		is_negated = True
		# Clean the lookup for Q object creation
		if spec.field_lookup_expression.startswith('!'):
			clean_lookup = spec.field_lookup_expression[1:]
		else: # starts with 'not '
			clean_lookup = spec.field_lookup_expression[4:]
		lookup = f"{spec.field_name}__{clean_lookup}"

	# Create the Q object
	q_object = Q(**{lookup: spec.field_lookup_value})

	# Apply negation if necessary
	if is_negated:
		return ~q_object
	return q_object

def tokenize(model: type[Model] | None, data_filter_query: str) -> tuple[int, bool, list[Token]|str]:
	"""
	Scans the query string and returns a list of Tokens or an error tuple.
	Supports "implicit AND" syntax.
	
	Returns:
		(final_index, is_success, list_of_tokens | error_message)
	"""
	idx = 0
	end_idx = len(data_filter_query) - 1
	last_token_type: TokenType|None = None
	tokens: list[Token] = []

	while idx <= end_idx:
		if len(tokens)==1 and last_token_type in (TokenType.LOGICAL_OP, TokenType.RPAREN):
			last_token = tokens[0]
			msg = f"""@idx={last_token.position} Expected {FIELD_LOOKUP_SPEC} or group_open_chars{list(GROUP_OPEN2CLOSE_CHARS.keys())} -> query can only start with {FIELD_LOOKUP_SPEC} or group_open_chars{list(GROUP_OPEN2CLOSE_CHARS.keys())} """
			return idx, False, msg
		
		# 1. Consume whitespace
		idx, _, _ = __consume_chars(data_filter_query, idx, end_idx, SPACE_CHARS)
		if idx > end_idx: break

		char = data_filter_query[idx]
		if char=='#': # Skip rest of the chars until new_line
			while idx <= end_idx and char!='\n':
				char = data_filter_query[idx]
				idx+=1
			continue
			
		start_pos = idx

		# 2. Check for Parentheses and IMPLICIT AND
		if char in GROUP_OPEN2CLOSE_CHARS:
			if last_token_type in (TokenType.FIELD_SPEC, TokenType.RPAREN):
				tokens.append(Token(TokenType.LOGICAL_OP, 'and', start_pos))
			
			tokens.append(Token(TokenType.LPAREN, char, start_pos))
			last_token_type = TokenType.LPAREN
			idx += 1
			continue
		
		elif char in GROUP_CLOSE2OPEN_CHARS:
			tokens.append(Token(TokenType.RPAREN, char, start_pos))
			last_token_type = TokenType.RPAREN
			idx += 1
			continue

		# 3. Check for Logical Operators
		new_idx, is_success, error_msg_or_op = __consume__logical_operator(data_filter_query, idx, end_idx)
		if is_success:
			tokens.append(Token(TokenType.LOGICAL_OP, error_msg_or_op, start_pos))
			last_token_type = TokenType.LOGICAL_OP
			idx = new_idx
			continue
		elif not is_success and len(tokens)>0 and last_token_type in (TokenType.RPAREN, TokenType.FIELD_SPEC):
			last_token = tokens[-1]
			msg = f"""@idx={new_idx} Expected logical_operator{list(LOGICAL_OPERATOR_PRECEDENCE.keys())} after '{last_token.value}' -> {error_msg_or_op}"""
			return new_idx, False, msg
		
		# 4. Assume it's a Field Specification
		new_idx, is_success, spec_or_error = __consume_field_spec(model, data_filter_query, idx, end_idx)
		if is_success:
			if last_token_type in (TokenType.FIELD_SPEC, TokenType.RPAREN):
				tokens.append(Token(TokenType.LOGICAL_OP, 'and', start_pos))
			
			tokens.append(Token(TokenType.FIELD_SPEC, spec_or_error, start_pos))
			last_token_type = TokenType.FIELD_SPEC
			idx = new_idx
			continue
		else:
			# On failure, return the error tuple
			error_msg = f"@idx={start_pos} Expected {FIELD_LOOKUP_SPEC} found '{data_filter_query[start_pos:new_idx]}' -> {spec_or_error}"
			return start_pos, False, error_msg
			
	return (idx, True, tokens)

def parse_and_build_q(model: type[Model] | None, data_filter_query: str) -> tuple[int, bool, Q|str]:
	"""
	Parses a filter query and builds a Django Q object in a single pass over the tokens.

	This function uses a direct evaluation method based on the Shunting-yard algorithm,
	which is more efficient as it avoids creating an intermediate AST.

	Returns:
		(final_index, is_success, q_object | error_message)
	"""
	# --- Phase 1: Tokenization ---
	idx, is_success, tokens_or_error = tokenize(model, data_filter_query)
	if not is_success:
		if isinstance(tokens_or_error, str):
			return (idx, False, tokens_or_error)
		else:
			return (idx, False, "An unexpected error occurred during tokenization.")
	
	if isinstance(tokens_or_error, str): # expected list[Token]
		return idx, False, tokens_or_error
	tokens: list[Token] = tokens_or_error
	
	# --- Phase 2: Direct Evaluation using Two Stacks ---
	operand_stack: list[Q] = []
	operator_stack: list[Token] = []
	LOGICAL_OPERATOR_PRECEDENCE = {'and': 2, 'or': 1}

	def apply_operator():
		"""Pops an operator and two operands, combines them, and pushes the result."""
		op_token = operator_stack.pop()
		if len(operand_stack) < 2:
			# Provide a specific error message
			msg = f"@idx={op_token.position} Not enough operands -> found '{op_token.value}' Expected >= 2 operands."
			operator_stack.append(op_token)
			raise ValueError(msg) # Internal exception for control flow
			
		right = operand_stack.pop()
		left = operand_stack.pop()

		if op_token.value == 'and':
			operand_stack.append(left & right)
		elif op_token.value == 'or':
			operand_stack.append(left | right)

	try:
		for token in tokens:
			if token.type == TokenType.FIELD_SPEC:
				operand_stack.append(_create_q_from_spec(token.value))

			elif token.type == TokenType.LPAREN:
				operator_stack.append(token)

			elif token.type == TokenType.RPAREN:
				while operator_stack and operator_stack[-1].type != TokenType.LPAREN:
					apply_operator()
				
				if not operator_stack or operator_stack[-1].type != TokenType.LPAREN:
					msg = f""""@idx={token.position} Mismatched parentheses -> found '{token.value}' without a matching '{GROUP_CLOSE2OPEN_CHARS[token.value]}'."""
					return (token.position, False, msg)
				operator_stack.pop() # Discard the '('

			elif token.type == TokenType.LOGICAL_OP:
				while (operator_stack and operator_stack[-1].type != TokenType.LPAREN and
					   LOGICAL_OPERATOR_PRECEDENCE.get(operator_stack[-1].value, 0) >= LOGICAL_OPERATOR_PRECEDENCE.get(token.value, 0)):
					apply_operator()
				operator_stack.append(token)

		# After loop, apply all remaining operators on the stack
		while operator_stack:
			op_token = operator_stack[-1]
			if op_token.type == TokenType.LPAREN:
				msg = f"""@idx={op_token.position} Mismatched parentheses -> Unclosed '{op_token.value}' found."""
				return (op_token.position, False, msg)
			apply_operator()

		# Final validation
		if len(operand_stack) != 1 or operator_stack:
			msg = f"""operand_stack={operand_stack}\noperator_stack={operand_stack}\n\t-> The final expression is malformed and could not be resolved."""
			return (len(data_filter_query), False, msg)

	except ValueError as e:
		op_token = operator_stack.pop()
		msg = str(e)
		return (op_token.position, False, msg)

	# Success!
	return (len(data_filter_query), True, operand_stack[0])


def query_model(model: type[Model], data_filter_query: str, queryset:QuerySet|None=None) -> tuple[int, bool, str | QuerySet]:
	"""
	Parses a query string, applies it to a Django model, and returns the QuerySet.

	This function handles both parsing errors from the query syntax and validation
	errors from the Django ORM, providing a single, clean interface for filtering.

	Args:
		model (Model): The Django model class to be queried.
		data_filter_query (str): The human-readable filter string.

	Returns:
		tuple[int, bool, str | QuerySet]: A tuple containing:
			- int: The index of the character where parsing stopped.
			- bool: True for success, False for failure.
			- str | QuerySet: A user-friendly error message on failure,
			  or the resulting Django QuerySet on success.
	"""
	# 1. Attempt to parse the query string into a Q object.
	# This will catch all syntax errors, invalid field names, and type mismatches.
	idx, is_success, result = parse_and_build_q(model, data_filter_query)
	
	if not is_success:
		# If parsing fails, the result is already a well-formatted error string.
		return idx, False, result #type:ignore
	
	# The result of a successful parse is the Q object.
	q_object = result
	
	# 2. Attempt to execute the query against the database.
	# This will catch semantic errors that the Django ORM can only find at runtime.
	try:
		# Use the successfully generated Q object to filter the model.
		if queryset is None:
			queryset = model.objects.filter(q_object)
		else:
			queryset = queryset.filter(q_object)
		
		# --- FORCE EVALUATION HERE ---
		# By calling .exists(), we force a database hit inside the try block.
		# This will trigger the ValueError if the query is invalid.
		queryset.exists() 

		return idx, True, queryset
		
	# Catch the most common Django ORM errors and format them nicely.
	except (FieldError, ValueError, ValidationError, TypeError) as e:
		# FieldError: "Cannot resolve keyword 'x' into field."
		# ValueError: Invalid value for a lookup, e.g., year='abc'.
		# ValidationError: From model field validation.
		# TypeError: Mismatched types in complex lookups.
		error_message = f"""ORM Validation Error: {e}\nParsed Query: {q_object}"""
		return idx, False, error_message
		
	# Catch any other unexpected exceptions as a safety net.
	except BaseException as e:
		error_message = f"An unexpected database error occurred: {e}"
		return idx, False, error_message
