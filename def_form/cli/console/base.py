from typing import Any

from rich.console import Console

from def_form.cli.context import CLIContext


class BaseConsole(Console):
    def __init__(self, context: CLIContext, *args: Any, **kwargs: Any) -> None:
        self.context = context
        super().__init__(*args, **kwargs)

    def info(self, message: str) -> None:
        raise NotImplementedError

    def success(self, message: str) -> None:
        raise NotImplementedError

    def warning(self, message: str) -> None:
        raise NotImplementedError

    def error(self, message: str) -> None:
        raise NotImplementedError

    def debug(self, message: str) -> None:
        raise NotImplementedError
