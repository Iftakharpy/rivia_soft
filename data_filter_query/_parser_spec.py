"""
query 1: ``
result: Model.objects.all()

query 2: `name contains "ali"`
result: Model.objects.filter( Q(name__contains="ali") )

query 3: `email endswith "@gmail.com" and name startswith "MD"`
result : Model.objects.filter( Q(email__endswith="@gmail.com") & Q(name__startswith="MD") )

query 4: `pk = 3`
result : Model.objects.filter( Q(pk=3) )

query 4: `likes_count >= 500 or comments_count >= 50`
result : Model.objects.filter( Q(likes_count__gte=500) | Q(comments_count__gte=50) )

query 5: `(((updated_at >= 2020-02-01 or updated_at <= 2011-02-01) and updated_at <= 2020-02-29) or (created_at >= 2020-01-01 and created_at <= 2020-01-31))`
result : Model.objects.filter( (Q(updated_at__gte=date(2020,02,01)) & Q((updated_at__lte=date(2020,02,01))) or (Q(created_at__gte=date(2020,01,01)) & Q((created_at__lte=date(2020,01,31))) )


Create a query parser for Field lookups which supports all field lookup expressions
like exact, iexact, regex, iregex, isnull, etc. which are supported by django 5.x

the parser should show proper error messages if the field doesn't exist on the model or the data type of the filed
doesn't match with the given data 





syntaxes

query: 


field_spec: [field_name] [whitespace] [lookup_operator] [whitespace] [field_value]
ex: is_active = True


field_name: r"[\w_]+" gm
ex: is_done, pk, client_id. Valid field names are from Model._meta.fields


lookup_operator: r"(?:==|=|>=|>|<=|<|[\w_]+)"gm
ex: ==, =, >=, >, <=, <,  ...more
	more from the parsed field_name Field.get_lookups().dict.keys()
Custom symbol mapping to lookups
{
	"==": "eq",
	"=": "eq",
	">=": "gte",
	">": "gt",
	"<=": "lte",
	"<": "lt",
}


field_value: r"(?:\"(?:\\\"|.)+?\")"gm
ex: None, 2, 2.3, "kd", 
types: None, bool, int, float, string, list
	can be attempted to parse to python using Field.get_prep_value(value)


	
logical_or: r"(?:\||or)"gmi
ex: |, or

logical_and: r"(?:&|and)"gmi
ex: &, and 


None: r"(?:None|null)"gmi
ex: None, none, Null, null

bool: [bool_true]|[bool_false]
ex: True, False, t, f, tRue, FaLsE

bool_true: r"(?:True|T)"gmi
ex: True, T, t, true

bool_false: r"(?:False|F)"gmi
ex: False, F, f, false


int: r"\d+"gm
ex: 00, 0212, 32329

float: r"\d+\.\d+"gm

string: r"(?:\"(?:\\\"|.)+?\")"gm
ex: "kk", "\kd", "sdkf .sadfklsf s.akffs,sadf3234 32\"dkf"

list: r"\[\s*(?:(?P<string>\"(?:\\\"|.)+?\")|(?P<float>\d+\.\d+)|(?P<int>\d+)|(?:\s*|,)*)+\s*\]"gmi
ex: 

whitespace: r"\s+"gm
"""



import re



def tokenize_with_position(expression):
    """
    Tokenizes the expression, yielding (token, start_position) tuples.
    Supports integers, floats, and single-character operators/brackets.
    """
    token_regex = re.compile(r'\d+(?:\.\d+)?|[+\-*/^]|\(|\)|\[|\]|\{|\}|\S')
    for match in token_regex.finditer(expression):
        yield (match.group(0), match.start())

def shunting_yard_final(expression):
    """
    Final, robust Shunting-yard algorithm.
    - Handles operator precedence and associativity.
    - Supports multiple bracket types: (), [], {}.
    - Provides specific error messages with positions.
    """
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
    associativity = {'+': 'L', '-': 'L', '*': 'L', '/': 'L', '^': 'R'}
    
    opening_brackets = "([{"
    closing_brackets = ")]}"
    bracket_map = {')': '(', ']': '[', '}': '{'}

    output_queue = []
    operator_stack = []
    
    for token, pos in tokenize_with_position(expression):
        if token.replace('.', '', 1).isdigit():
            output_queue.append(float(token))
        elif token in precedence:
            while (operator_stack and operator_stack[-1] not in opening_brackets and
                   (precedence.get(operator_stack[-1], 0) > precedence[token] or
                    (precedence.get(operator_stack[-1], 0) == precedence[token] and associativity[token] == 'L'))):
                output_queue.append(operator_stack.pop())
            operator_stack.append(token)
        elif token in opening_brackets:
            operator_stack.append(token)
        elif token in closing_brackets:
            # Process operators inside the current bracket group.
            while operator_stack and operator_stack[-1] not in opening_brackets:
                output_queue.append(operator_stack.pop())
            
            # Check for a matching opening bracket.
            if not operator_stack:
                raise SyntaxError(f"Mismatched closing bracket '{token}' at position {pos}. No opening bracket was found.")
            
            opener = operator_stack.pop() # Pop the opening bracket.
            if opener != bracket_map[token]:
                raise SyntaxError(f"Mismatched closing bracket '{token}' at position {pos}. Expected a match for '{opener}' which was opened earlier.")
        else:
            raise SyntaxError(f"Invalid or unknown token '{token}' at position {pos}.")

    # After processing all tokens, check the stack.
    while operator_stack:
        op = operator_stack.pop()
        if op in opening_brackets:
            raise SyntaxError(f"Unclosed opening bracket '{op}' at end of expression.")
        output_queue.append(op)

    return output_queue


# Uses the same `tokenize_with_position` function from above.

def pratt_parser_final(expression):
    """
    Final, robust iterative Pratt-style parser.
    - Directly evaluates the expression.
    - Supports multiple bracket types: (), [], {}.
    - Provides specific error messages with positions.
    """
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
    opening_brackets = "([{"
    closing_brackets = ")]}"
    bracket_map = {')': '(', ']': '[', '}': '{'}
    
    tokens_with_pos = list(tokenize_with_position(expression))
    
    operand_stack = []
    operator_stack = []

    def apply_operator():
        if len(operand_stack) < 2:
            op = operator_stack[-1] if operator_stack else "an operation"
            raise SyntaxError(f"Invalid syntax near '{op}'. Not enough operands available.")
        
        operator = operator_stack.pop()
        right = operand_stack.pop()
        left = operand_stack.pop()

        if operator == '+': operand_stack.append(left + right)
        elif operator == '-': operand_stack.append(left - right)
        elif operator == '*': operand_stack.append(left * right)
        elif operator == '/':
            if right == 0:
                raise ZeroDivisionError("Division by zero.")
            operand_stack.append(left / right)

    for token, pos in tokens_with_pos:
        if token.replace('.', '', 1).isdigit():
            operand_stack.append(float(token))
        elif token in precedence:
            while (operator_stack and 
                   operator_stack[-1] not in opening_brackets and 
                   precedence.get(operator_stack[-1], 0) >= precedence[token]):
                apply_operator()
            operator_stack.append(token)
        elif token in opening_brackets:
            operator_stack.append(token)
        elif token in closing_brackets:
            while operator_stack and operator_stack[-1] not in opening_brackets:
                apply_operator()
            
            if not operator_stack:
                raise SyntaxError(f"Mismatched closing bracket '{token}' at position {pos}. No opening bracket was found.")
            
            opener = operator_stack.pop() # Pop the opening bracket.
            if opener != bracket_map[token]:
                raise SyntaxError(f"Mismatched closing bracket '{token}' at position {pos}. Expected a match for '{opener}'.")
        else:
            raise SyntaxError(f"Invalid or unknown token '{token}' at position {pos}.")

    while operator_stack:
        op = operator_stack[-1]
        if op in opening_brackets:
             raise SyntaxError(f"Unclosed opening bracket '{op}' at end of expression.")
        apply_operator()
        
    if len(operand_stack) != 1 or operator_stack:
        raise SyntaxError("The expression is malformed and could not be resolved to a single value.")

    return operand_stack[0]

