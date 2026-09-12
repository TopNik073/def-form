from def_form.exceptions.base import BaseDefFormException
from def_form.exceptions.cache import ToolVersionNotFoundException
from def_form.exceptions.def_formatter import TooManyInlineArgumentsException


def test_str_includes_message_and_path() -> None:
    exc = TooManyInlineArgumentsException(path='src/a.py:12', message='Too many inline args')

    assert str(exc) == 'Too many inline args: src/a.py:12'


def test_str_falls_back_to_message_without_path() -> None:
    exc = BaseDefFormException(path='', message='something went wrong')

    assert str(exc) == 'something went wrong'


def test_tool_version_exception_has_a_default_message() -> None:
    exc = ToolVersionNotFoundException(path='def-form')

    assert 'def-form version' in str(exc)
