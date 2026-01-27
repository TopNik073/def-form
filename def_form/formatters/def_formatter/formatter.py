from typing import Any, cast

from libcst import Comma
from libcst import Comment
from libcst import CSTTransformer
from libcst import FunctionDef
from libcst import Param
from libcst import Parameters
from libcst import ParenthesizedWhitespace
from libcst import SimpleWhitespace
from libcst import TrailingWhitespace

from def_form.formatters.def_formatter.base import DefBase


class DefFormatter(DefBase, CSTTransformer):
    def __init__(
        self, filepath: str, max_def_length: int | None, max_inline_args: int | None, indent_size: int | None = None
    ):
        super().__init__(filepath, max_def_length, max_inline_args)
        self.indent_size = indent_size if indent_size is not None else 4

    def _is_valid_param(self, param: Any) -> bool:
        return isinstance(param, Param)

    def _extract_comment_from_whitespace(self, ws: Any) -> TrailingWhitespace | None:
        if isinstance(ws, TrailingWhitespace):
            return ws
        if isinstance(ws, ParenthesizedWhitespace) and isinstance(ws.first_line, TrailingWhitespace):
            return ws.first_line
        if isinstance(ws, SimpleWhitespace) and '#' in ws.value:
            parts = ws.value.split('#', 1)
            spaces = parts[0].rstrip()
            comment_text = '#' + parts[1].rstrip()
            return TrailingWhitespace(
                whitespace=SimpleWhitespace(spaces + ' ' if spaces else ''), comment=Comment(comment_text)
            )
        return None

    def _extract_comment_from_param(self, param: Param) -> TrailingWhitespace | None:
        if isinstance(param.comma, Comma) and param.comma.whitespace_after:
            comment = self._extract_comment_from_whitespace(param.comma.whitespace_after)
            if comment:
                return comment
        if param.whitespace_after_param:
            return self._extract_comment_from_whitespace(param.whitespace_after_param)
        return None

    def _create_whitespace(
        self, comment: TrailingWhitespace | None, last_line: SimpleWhitespace
    ) -> ParenthesizedWhitespace:
        if comment:
            return ParenthesizedWhitespace(first_line=comment, empty_lines=[], indent=True, last_line=last_line)
        return ParenthesizedWhitespace(last_line=last_line, indent=True)

    def _create_formatted_param_for_single_line(self, param: Param, is_last: bool = False) -> Param:
        indent = ' ' * self.indent_size
        comment = self._extract_comment_from_param(param)
        last_line = SimpleWhitespace('' if is_last else indent)
        new_ws = self._create_whitespace(comment, last_line)
        need_comma = param.comma is not None if is_last else True
        new_comma = Comma(whitespace_after=new_ws) if need_comma else None
        return param.with_changes(comma=new_comma, whitespace_after_param=SimpleWhitespace(''))

    def _create_formatted_param_for_multi_line(self, param: Param, is_last: bool = False) -> Param:
        indent = ' ' * self.indent_size
        last_line = SimpleWhitespace('' if is_last else indent)
        original_ws = param.comma.whitespace_after if isinstance(param.comma, Comma) else None

        if isinstance(original_ws, ParenthesizedWhitespace):
            comment = original_ws.first_line if isinstance(original_ws.first_line, TrailingWhitespace) else None
            new_ws = self._create_whitespace(comment, last_line)
        elif isinstance(original_ws, TrailingWhitespace):
            new_ws = self._create_whitespace(original_ws, last_line)
        else:
            new_ws = self._create_whitespace(None, last_line)

        need_comma = param.comma is not None if is_last else True
        new_comma = Comma(whitespace_after=new_ws) if need_comma else None
        return param.with_changes(comma=new_comma, whitespace_after_param=SimpleWhitespace(''))

    def _collect_all_params(self, node: FunctionDef) -> list[Param]:
        all_params: list[Param] = list(node.params.params)

        if self._is_valid_param(node.params.star_arg):
            all_params.append(cast(Param, node.params.star_arg))

        all_params.extend(node.params.kwonly_params)

        if self._is_valid_param(node.params.star_kwarg):
            all_params.append(cast(Param, node.params.star_kwarg))

        return all_params

    def _restore_param_groups(self, formatted_params: list[Param], node: FunctionDef) -> tuple:
        param_count = len(node.params.params)
        kwonly_count = len(node.params.kwonly_params)
        new_params = formatted_params[:param_count]
        remaining = formatted_params[param_count:]

        new_star_arg = None
        if self._is_valid_param(node.params.star_arg) and remaining:
            new_star_arg = remaining[0]
            remaining = remaining[1:]

        new_kwonly_params = remaining[:kwonly_count] if kwonly_count else []
        remaining = remaining[kwonly_count:]

        new_star_kwarg = None
        if self._is_valid_param(node.params.star_kwarg) and remaining:
            new_star_kwarg = remaining[0]

        return new_params, new_kwonly_params, new_star_arg, new_star_kwarg

    def _process_parameters(self, node: FunctionDef, is_single_line: bool) -> FunctionDef:
        all_params = self._collect_all_params(node)
        total_params = len(all_params)
        format_func = (
            self._create_formatted_param_for_single_line
            if is_single_line
            else self._create_formatted_param_for_multi_line
        )
        formatted_params = [format_func(param, i == total_params - 1) for i, param in enumerate(all_params)]
        new_params, new_kwonly_params, new_star_arg, new_star_kwarg = self._restore_param_groups(formatted_params, node)

        return node.with_changes(
            params=Parameters(
                params=new_params,
                posonly_params=node.params.posonly_params,
                kwonly_params=new_kwonly_params,
                star_arg=new_star_arg,
                star_kwarg=new_star_kwarg,
            ),
            whitespace_before_params=ParenthesizedWhitespace(
                last_line=SimpleWhitespace(' ' * self.indent_size), indent=True
            ),
        )

    def leave_FunctionDef(self, original_node: FunctionDef, updated_node: FunctionDef) -> FunctionDef:
        analysis = self.analyze_function(original_node)
        if not analysis.should_process:
            return updated_node
        if analysis.issues:
            self.issues.extend(analysis.issues)
        return self._process_parameters(updated_node, self.is_single_line_function(original_node))
