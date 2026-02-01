from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from def_form.exceptions.base import BaseDefFormException


class BaseUI(ABC):
    @abstractmethod
    def show_config_info(self, **config: Any) -> None:
        raise NotImplemented

    @abstractmethod
    def start(self, total: int | None) -> None:
        raise NotImplemented

    @abstractmethod
    def processing(self, path: Path) -> None:
        raise NotImplemented

    @abstractmethod
    def skipped(self, path: Path) -> None:
        raise NotImplemented

    @abstractmethod
    def finish(self, processed: int, issues: list[BaseDefFormException]) -> None:
        raise NotImplemented

    @abstractmethod
    def show_issues(self, processed: int, issues: list[BaseDefFormException]) -> None:
        raise NotImplemented

    @abstractmethod
    def show_summary(self, processed: int, issues: list[BaseDefFormException]) -> None:
        raise NotImplemented
