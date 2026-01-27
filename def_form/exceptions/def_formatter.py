from dataclasses import dataclass

from def_form.exceptions.base import BaseDefFormException


@dataclass
class BaseDefFormatterException(BaseDefFormException):
    path: str
    message: str
    description: str | None = None


@dataclass
class DefStringTooLongException(BaseDefFormException):
    path: str
    message: str = 'String is too long'
    description: str | None = None


@dataclass
class TooManyInlineArgumentsException(BaseDefFormException):
    path: str
    message: str = 'Too many inline arguments'
    description: str | None = None


@dataclass
class InvalidMultilineParamsIndentException(BaseDefFormException):
    path: str
    message: str = 'Invalid multiline params indentation'
    description: str | None = None
