from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from def_form.cli.console import BaseConsole
from def_form.cli.context import CLIContext
from def_form.exceptions.base import BaseDefFormException


class BaseUI(ABC):
    def __init__(self, console: BaseConsole) -> None:
        self.console: BaseConsole = console
        self.context: CLIContext = console.context

    @abstractmethod
    def show_config_info(self, **config: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def start(self, total: int | None) -> None:
        raise NotImplementedError

    @abstractmethod
    def processing(self, path: Path) -> None:
        raise NotImplementedError

    @abstractmethod
    def skipped(self, path: Path) -> None:
        raise NotImplementedError

    @abstractmethod
    def finish(self, processed: int, issues: list[BaseDefFormException]) -> None:
        raise NotImplementedError

    @abstractmethod
    def show_issues(self, processed: int, issues: list[BaseDefFormException]) -> None:
        raise NotImplementedError

    @abstractmethod
    def show_summary(self, processed: int, issues: list[BaseDefFormException]) -> None:
        raise NotImplementedError
