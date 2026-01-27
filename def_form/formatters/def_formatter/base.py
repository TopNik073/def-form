import re
from pathlib import Path
from typing import cast

from libcst import FunctionDef, Comma
from libcst import MetadataDependent
from libcst import Module
from libcst import Param
from libcst import ParenthesizedWhitespace
from libcst import SimpleWhitespace
from libcst.matchers import BaseParenthesizableWhitespace
from libcst.metadata import PositionProvider

from def_form.exceptions.base import BaseDefFormException
from def_form.exceptions.def_formatter import DefStringTooLongException
from def_form.exceptions.def_formatter import InvalidMultilineParamsIndentException
from def_form.exceptions.def_formatter import TooManyInlineArgumentsException
from def_form.formatters.def_formatter.models import FunctionAnalysis


class DefBase(MetadataDependent):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(
        self, filepath: str, max_def_length: int | None, max_inline_args: int | None, indent_size: int | None = None
    ):
        super().__init__()
        self.filepath = filepath
        self.max_def_length = max_def_length
        self.max_inline_args = max_inline_args
        self.indent_size = indent_size if indent_size is not None else 4
        self.issues: list[BaseDefFormException] = []

    def _check_issues(self, line_length: int, line_no: int, arg_count: int) -> list[BaseDefFormException]:
        issues: list[BaseDefFormException] = []

        if self.max_def_length and line_length > self.max_def_length:
            issues.append(
                DefStringTooLongException(
                    path=f'{self.filepath}:{line_no}',
                    message=f'Function definition too long ({line_length} > {self.max_def_length})',
                )
            )

        if self.max_inline_args and arg_count > self.max_inline_args:
            issues.append(
                TooManyInlineArgumentsException(
                    path=f'{self.filepath}:{line_no}',
                    message=f'Too many inline args ({arg_count} > {self.max_inline_args})',
                )
            )

        return issues

    def is_single_line_function(self, node: FunctionDef) -> bool:
        func_code = Module([]).code_for_node(node).strip()
        lines = func_code.split('\n')

        for line in lines:
            if line.strip().startswith(('def ', 'async def ')):
                clean_line = re.sub(r'#.*', '', line)
                return ')' in clean_line and ':' in clean_line

        return False

    def has_skip_comment(self, node: FunctionDef) -> bool:
        pos = self.get_metadata(PositionProvider, node)

        try:
            with Path.open(Path(self.filepath), encoding='utf-8') as f:
                lines = f.readlines()
        except (OSError, UnicodeDecodeError):
            return False

        def_line = lines[pos.start.line - 1]
        if '# def-form: skip' in def_line.lower():
            return True

        if pos.start.line > 1:
            prev_line = lines[pos.start.line - 2]
            if '# def-form: skip' in prev_line.lower():
                return True

        return False

    def _get_params_list(self, node: FunctionDef) -> list[Param]:
        params: list[Param] = []
        params.extend(node.params.params)

        if isinstance(node.params.star_arg, Param):
            params.append(node.params.star_arg)

        params.extend(node.params.kwonly_params)

        if isinstance(node.params.star_kwarg, Param):
            params.append(node.params.star_kwarg)

        return params

    def has_correct_multiline_params_format(self, node: FunctionDef) -> bool:  # noqa: PLR0911, PLR0912
        ws = node.whitespace_before_params
        if not isinstance(ws, ParenthesizedWhitespace):
            return False

        if not ws.indent:
            return False

        if not isinstance(ws.last_line, SimpleWhitespace):
            return False

        expected_indent = ' ' * self.indent_size
        if ws.last_line.value != expected_indent:
            return False

        all_params = self._get_params_list(node)

        if not all_params:
            return True

        for param in all_params[:-1]:
            comma = param.comma
            if not isinstance(comma, Comma):
                return False

            ws_after = cast(BaseParenthesizableWhitespace, comma.whitespace_after)
            if not isinstance(ws_after, ParenthesizedWhitespace):
                return False

            if not ws_after.indent:
                return False

            if not isinstance(ws_after.last_line, SimpleWhitespace):
                return False

            if ws_after.last_line.value != expected_indent:
                return False

        last_param = all_params[-1]
        comma = last_param.comma
        if not isinstance(comma, Comma):
            return False

        ws_after = cast(BaseParenthesizableWhitespace, comma.whitespace_after)
        if not isinstance(ws_after, ParenthesizedWhitespace):
            return False

        if not ws_after.indent:
            return False

        if not isinstance(ws_after.last_line, SimpleWhitespace):
            return False

        return ws_after.last_line.value == ''

    def _count_arguments(self, node: FunctionDef) -> int:
        count = len(node.params.params)

        if isinstance(node.params.star_arg, Param):
            count += 1

        count += len(node.params.kwonly_params)

        if isinstance(node.params.star_kwarg, Param):
            count += 1

        return count

    def analyze_function(self, node: FunctionDef) -> FunctionAnalysis:
        if self.has_skip_comment(node):
            return FunctionAnalysis(
                should_process=False,
                reason='skip_comment',
                node=node,
            )

        func_code = Module([]).code_for_node(node).strip()
        first_line = func_code.split('\n')[0]
        line_length = len(first_line)

        arg_count = self._count_arguments(node)

        if arg_count == 0:
            return FunctionAnalysis(
                should_process=False,
                reason='no_args',
                node=node,
                line_length=line_length,
                arg_count=arg_count,
            )

        pos = self.get_metadata(PositionProvider, node)
        line_no = pos.start.line

        issues: list[BaseDefFormException] = []

        if self.is_single_line_function(node):
            issues = self._check_issues(line_length, line_no, arg_count)
        elif not self.has_correct_multiline_params_format(node):
            issues.append(
                InvalidMultilineParamsIndentException(
                    path=f'{self.filepath}:{line_no}',
                    message=f'Invalid multiline function parameters indentation (expected {self.indent_size} spaces)',
                )
            )

        has_issues = bool(issues)

        return FunctionAnalysis(
            should_process=has_issues,
            line_length=line_length,
            arg_count=arg_count,
            line_no=line_no,
            pos=pos,
            node=node,
            issues=issues,
        )
