from dataclasses import dataclass


@dataclass
class BaseDefFormException(Exception):
    path: str
    message: str
    description: str | None = None
