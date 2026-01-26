from dataclasses import dataclass


@dataclass
class BaseDefFormException(Exception):
    path: str | None = None
    message: str | None = None
    description: str | None = None
