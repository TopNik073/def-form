from pathlib import Path
from typing import Any

from def_form.cli.ui import BaseUI
from def_form.exceptions.base import BaseDefFormException


class NullUI(BaseUI):
    def show_config_info(self, **config: Any) -> None:
        return

    def start(self, total: int | None) -> None:
        return

    def processing(self, path: Path) -> None:
        return

    def skipped(self, path: Path) -> None:
        return

    def finish(self, processed: int, issues: list[BaseDefFormException]) -> None:
        return

    def show_issues(self, processed: int, issues: list[BaseDefFormException]) -> None:
        return

    def show_summary(self, processed: int, issues: list[BaseDefFormException]) -> None:
        return
