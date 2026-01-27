from dataclasses import dataclass

from libcst import FunctionDef
from libcst._position import CodeRange

from def_form.exceptions.base import BaseDefFormException


@dataclass
class FunctionAnalysis:
    """Результат анализа функции."""

    should_process: bool
    reason: str | None = None
    line_length: int | None = None
    arg_count: int | None = None
    line_no: int | None = None
    pos: CodeRange | None = None
    node: FunctionDef | None = None
    issues: list[BaseDefFormException] | None = None

    def __post_init__(self) -> None:
        if self.issues is None:
            self.issues = []
