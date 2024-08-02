from django.core.validators import RegexValidator
import re


# UTR number
UTR_REGEX = r'^[0-9]{10}$'
COMPILED_UTR_REGEX = re.compile(UTR_REGEX)
# Validator
UTR_VALIDATOR = RegexValidator(
    regex=COMPILED_UTR_REGEX,
    message='Enter 10 digit UTR Number',
    code='Invalid UTR')

# NINO
# https://www.gov.uk/hmrc-internal-manuals/national-insurance-manual/nim39110
# explicit
NINO_REGEX = r'^(?!BG|GB|KN|NK|NT|TN|ZZ)[ABCEGHJKLMNOPRSTWXYZ][ABCEGHJKLMNPRSTWXYZ][0-9]{6}[ABCD]$'
COMPILED_NINO_REGEX = re.compile(NINO_REGEX, flags=re.IGNORECASE)
NINO_VALIDATOR = RegexValidator(
    regex=COMPILED_NINO_REGEX,
    message='Enter 9 chars long NINO.',
    code='Invalid NINO')

# Sort Code
SORT_CODE_REGEX = r'^[0-9]{6}$'
COMPILED_SORT_CODE_REGEX = re.compile(SORT_CODE_REGEX)
SORT_CODE_VALIDATOR = RegexValidator(
    regex=COMPILED_SORT_CODE_REGEX,
    message='Enter 6 digit Sort Code',
    code='Invalid Sort Code')

# Bank Account Number
BANK_ACCOUNT_NUMBER_REGEX = r'^[0-9]{8}$'
COMPILED_BANK_ACCOUNT_NUMBER = re.compile(BANK_ACCOUNT_NUMBER_REGEX)
BANK_ACCOUNT_NUMBER_VALIDATOR = RegexValidator(
    regex=COMPILED_BANK_ACCOUNT_NUMBER,
    message='Enter 8 digit Bank Account Number',
    code='Invalid Bank Account'
)

# company_auth_code
AUTH_CODE_REGEX = r'^[A-Za-z0-9]{6}$'
COMPILED_AUTH_CODE_REGEX = re.compile(AUTH_CODE_REGEX)
# Validator
AUTH_CODE_VALIDATOR = RegexValidator(
    regex=COMPILED_AUTH_CODE_REGEX,
    message='Enter 6 digit alphanumeric code',
    code='Invalid company authentication code')


# tax_year
TAX_YEAR_REGEX = r'^\d{4}-\d{4}$'
COMPILED_TAX_YEAR_REGEX = re.compile(TAX_YEAR_REGEX)
# validator
TAX_YEAR_VALIDATOR = RegexValidator(
    regex=COMPILED_TAX_YEAR_REGEX,
    message="Maintain the format(dddd-dddd) for tax years. Ex: 2020-2021"
)

# alphanumeric_file_number
ALPHANUMERIC_FILE_NUMBER_REGEX = r"([A-Z0-9]{4,16})"
ALPHANUMERIC_FILE_NUMBER_VALIDATOR = RegexValidator(
    regex=ALPHANUMERIC_FILE_NUMBER_REGEX,
    message="The length has to be between 4 and 16 characters and allowed characters are A-Z and 0-9.")
ALPHANUMERIC_FILE_NUMBER_VALIDATORS = [ALPHANUMERIC_FILE_NUMBER_VALIDATOR, 
                                       RegexValidator(regex=r"[A-Z]", message="Must contain a character from A-Z."), 
                                       RegexValidator(regex=r"[0-9]", message="Must contain a digit from 0-9."),
                                       RegexValidator(regex=r"[^A-Z0-9]", message="Have you used something other than A-Z or 0-9?", inverse_match=True),
                                       ]