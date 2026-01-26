from def_form.exceptions.def_formatter import DefStringTooLongException
from def_form.exceptions.def_formatter import TooManyInlineArgumentsException
from tests.constants import EXAMPLE_PATH

EXPECTED_ISSUES: list[DefStringTooLongException | TooManyInlineArgumentsException] = [
    TooManyInlineArgumentsException(
        path=f'{EXAMPLE_PATH}:19', message='Too many inline args (5 > 2)', description=None
    ),
    TooManyInlineArgumentsException(
        path=f'{EXAMPLE_PATH}:25', message='Too many inline args (4 > 2)', description=None
    ),
    TooManyInlineArgumentsException(
        path=f'{EXAMPLE_PATH}:28', message='Too many inline args (5 > 2)', description=None
    ),
    TooManyInlineArgumentsException(
        path=f'{EXAMPLE_PATH}:31', message='Too many inline args (4 > 2)', description=None
    ),
    TooManyInlineArgumentsException(
        path=f'{EXAMPLE_PATH}:34', message='Too many inline args (3 > 2)', description=None
    ),
    TooManyInlineArgumentsException(
        path=f'{EXAMPLE_PATH}:42', message='Too many inline args (4 > 2)', description=None
    ),
    TooManyInlineArgumentsException(
        path=f'{EXAMPLE_PATH}:58', message='Too many inline args (4 > 2)', description=None
    ),
    DefStringTooLongException(
        path=f'{EXAMPLE_PATH}:61', message='Function definition too long (165 > 100)', description=None
    ),
    DefStringTooLongException(
        path=f'{EXAMPLE_PATH}:64', message='Function definition too long (163 > 100)', description=None
    ),
    DefStringTooLongException(
        path=f'{EXAMPLE_PATH}:67', message='Function definition too long (126 > 100)', description=None
    ),
    TooManyInlineArgumentsException(
        path=f'{EXAMPLE_PATH}:75', message='Too many inline args (4 > 2)', description=None
    ),
    TooManyInlineArgumentsException(
        path=f'{EXAMPLE_PATH}:78', message='Too many inline args (5 > 2)', description=None
    ),
    TooManyInlineArgumentsException(
        path=f'{EXAMPLE_PATH}:84', message='Too many inline args (5 > 2)', description=None
    ),
    TooManyInlineArgumentsException(
        path=f'{EXAMPLE_PATH}:88', message='Too many inline args (5 > 2)', description=None
    ),
    TooManyInlineArgumentsException(
        path=f'{EXAMPLE_PATH}:103', message='Too many inline args (5 > 2)', description=None
    ),
    TooManyInlineArgumentsException(
        path=f'{EXAMPLE_PATH}:110', message='Too many inline args (6 > 2)', description=None
    ),
    TooManyInlineArgumentsException(
        path=f'{EXAMPLE_PATH}:113', message='Too many inline args (3 > 2)', description=None
    ),
    DefStringTooLongException(
        path=f'{EXAMPLE_PATH}:116', message='Function definition too long (174 > 100)', description=None
    ),
    DefStringTooLongException(
        path=f'{EXAMPLE_PATH}:119', message='Function definition too long (199 > 100)', description=None
    ),
    TooManyInlineArgumentsException(
        path=f'{EXAMPLE_PATH}:119', message='Too many inline args (5 > 2)', description=None
    ),
    DefStringTooLongException(
        path=f'{EXAMPLE_PATH}:122', message='Function definition too long (127 > 100)', description=None
    ),
    DefStringTooLongException(
        path=f'{EXAMPLE_PATH}:125', message='Function definition too long (138 > 100)', description=None
    ),
    TooManyInlineArgumentsException(
        path=f'{EXAMPLE_PATH}:125', message='Too many inline args (3 > 2)', description=None
    ),
]
