from dataclasses import dataclass


@dataclass
class BaseDefFormException(Exception):
    path: str
    message: str
    description: str | None = None

    def __str__(self) -> str:
        return f'{self.message}: {self.path}' if self.path else self.message
