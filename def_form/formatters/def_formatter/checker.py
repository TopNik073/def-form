from libcst import CSTVisitor
from libcst import FunctionDef

from def_form.formatters.def_formatter.base import DefBase


class DefChecker(DefBase, CSTVisitor):
    def __init__(
        self,
        filepath: str,
        max_def_length: int | None,
        max_inline_args: int | None,
        indent_size: int | None,
    ):
        super().__init__(
            filepath=filepath,
            max_def_length=max_def_length,
            max_inline_args=max_inline_args,
            indent_size=indent_size,
        )

    def leave_FunctionDef(self, original_node: FunctionDef) -> None:
        analysis = self.analyze_function(original_node)

        if analysis.issues:
            self.issues.extend(analysis.issues)
