from dataclasses import dataclass

from def_form.exceptions.base import BaseDefFormException


@dataclass
class ToolVersionNotFoundException(BaseDefFormException):
    path: str
    message: str = 'Unable to determine the installed def-form version'
    description: str | None = None
