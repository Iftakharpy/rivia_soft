from django import template

register = template.Library()


@register.filter(name="as_percentage_of")
def as_percentage_of(number, percentage):
    try:
        return (float(number) * percentage) / 100
    except (ValueError, ZeroDivisionError):
        return 0
    except (Exception):
        return "Error"

@register.filter(name="subtract")
def subtract(number1, number2):
    try:
        return float(number1) - float(number2)
    except Exception:
        return "Error"

@register.filter(name="add")
def add(number1, number2):
    try:
        return float(number1) + float(number2)
    except Exception:
        return "Error"


@register.filter(name="natural_round")
def natural_round(number):
    try:
        number = float(number)

        # Cascade rounding the floating digits from right to left
        floating_digits = [int(digit) for digit in str(number).split(".")[-1]]
        idx = len(floating_digits)-1
        while idx > 0:
            if floating_digits[idx]>=5:
                floating_digits[idx-1] += 1
            idx -= 1
        
        # Cascade round to the integer part
        number = int(number)
        if floating_digits[0] >= 5:
            number += 1
        
        return number
    except Exception:
        return "Error"

@register.simple_tag(name="round_str")
def round_str(number, **kwargs):
    try:
        digits = 0
        if "digits" in kwargs:
            digits = int(kwargs["digits"])
        return f"{round(float(number))}{ '.'+'0'*digits if digits>0 else ''}"
    except Exception as e:
        print(e)
        return "Error"
