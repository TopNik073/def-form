from libcst import CSTTransformer
from libcst import FunctionDef

from def_form.core.base import DefBase
from def_form.core.node_builder import build_parameters


class DefFormatter(DefBase, CSTTransformer):
    def __init__(
        self,
        filepath: str,
        max_def_length: int | None,
        max_inline_args: int | None,
        indent_size: int | None = None,
    ):
        super().__init__(
            filepath=filepath,
            max_def_length=max_def_length,
            max_inline_args=max_inline_args,
            indent_size=indent_size,
        )

    def leave_FunctionDef(self, original_node: FunctionDef, updated_node: FunctionDef) -> FunctionDef:
        analysis = self.analyze_function(original_node)
        if not analysis.should_process:
            return updated_node
        if analysis.issues:
            self.issues.extend(analysis.issues)
        is_single_line = self.is_single_line_function(original_node)
        params, whitespace_before_params = build_parameters(
            updated_node,
            is_single_line=is_single_line,
            indent_size=self.indent_size,
        )
        return updated_node.with_changes(
            params=params,
            whitespace_before_params=whitespace_before_params,
        )
