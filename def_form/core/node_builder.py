from typing import Any

from libcst import Comma, MaybeSentinel
from libcst import Comment
from libcst import FunctionDef
from libcst import Param
from libcst import Parameters
from libcst import ParenthesizedWhitespace
from libcst import SimpleWhitespace
from libcst import TrailingWhitespace

from def_form.core.params import get_params_list


def _is_valid_param(param: Any) -> bool:
    return isinstance(param, Param)


def _extract_comment_from_whitespace(ws: Any) -> TrailingWhitespace | None:
    if isinstance(ws, TrailingWhitespace):
        return ws
    if isinstance(ws, ParenthesizedWhitespace) and isinstance(ws.first_line, TrailingWhitespace):
        return ws.first_line
    if isinstance(ws, SimpleWhitespace) and '#' in ws.value:
        parts = ws.value.split('#', 1)
        spaces = parts[0].rstrip()
        comment_text = '#' + parts[1].rstrip()
        return TrailingWhitespace(
            whitespace=SimpleWhitespace(spaces + ' ' if spaces else ''),
            comment=Comment(comment_text),
        )
    return None


def _extract_comment_from_param(param: Param) -> TrailingWhitespace | None:
    if isinstance(param.comma, Comma) and param.comma.whitespace_after:
        comment = _extract_comment_from_whitespace(param.comma.whitespace_after)
        if comment:
            return comment
    if param.whitespace_after_param:
        return _extract_comment_from_whitespace(param.whitespace_after_param)
    return None


def _create_whitespace(
    indent_size: int,
    comment: TrailingWhitespace | None,
    last_line: SimpleWhitespace,
) -> ParenthesizedWhitespace:
    if comment:
        return ParenthesizedWhitespace(first_line=comment, empty_lines=[], indent=True, last_line=last_line)
    return ParenthesizedWhitespace(last_line=last_line, indent=True)


def _create_formatted_param_for_single_line(
    indent_size: int,
    param: Param,
    is_last: bool = False,
) -> Param:
    indent = ' ' * indent_size
    comment = _extract_comment_from_param(param)
    last_line = SimpleWhitespace('' if is_last else indent)
    new_ws = _create_whitespace(indent_size, comment, last_line)
    need_comma = param.comma is not None if is_last else True
    new_comma = Comma(whitespace_after=new_ws) if need_comma else None
    return param.with_changes(comma=new_comma, whitespace_after_param=SimpleWhitespace(''))


def _create_formatted_param_for_multi_line(
    indent_size: int,
    param: Param,
    is_last: bool = False,
) -> Param:
    indent = ' ' * indent_size
    last_line = SimpleWhitespace('' if is_last else indent)
    original_ws = param.comma.whitespace_after if isinstance(param.comma, Comma) else None

    if isinstance(original_ws, ParenthesizedWhitespace):
        comment = original_ws.first_line if isinstance(original_ws.first_line, TrailingWhitespace) else None
        new_ws = _create_whitespace(indent_size, comment, last_line)
    elif isinstance(original_ws, TrailingWhitespace):
        new_ws = _create_whitespace(indent_size, original_ws, last_line)
    else:
        new_ws = _create_whitespace(indent_size, None, last_line)

    need_comma = param.comma is not None if is_last else True
    new_comma = Comma(whitespace_after=new_ws) if need_comma else None
    return param.with_changes(comma=new_comma, whitespace_after_param=SimpleWhitespace(''))


def _restore_param_groups(
    formatted_params: list[Param],
    node: FunctionDef,
) -> tuple[list[Param], list[Param], Param | None, Param | None]:
    param_count = len(node.params.params)
    kwonly_count = len(node.params.kwonly_params)
    new_params = formatted_params[:param_count]
    remaining = formatted_params[param_count:]

    new_star_arg = None
    if _is_valid_param(node.params.star_arg) and remaining:
        new_star_arg = remaining[0]
        remaining = remaining[1:]

    new_kwonly_params = remaining[:kwonly_count] if kwonly_count else []
    remaining = remaining[kwonly_count:]

    new_star_kwarg = None
    if _is_valid_param(node.params.star_kwarg) and remaining:
        new_star_kwarg = remaining[0]

    return new_params, new_kwonly_params, new_star_arg, new_star_kwarg


def build_parameters(
    node: FunctionDef,
    is_single_line: bool,
    indent_size: int,
) -> tuple[Parameters, ParenthesizedWhitespace]:
    all_params = get_params_list(node)
    total_params = len(all_params)
    if is_single_line:
        format_param = lambda p, last: _create_formatted_param_for_single_line(indent_size, p, last)
    else:
        format_param = lambda p, last: _create_formatted_param_for_multi_line(indent_size, p, last)
    formatted_params = [format_param(param, i == total_params - 1) for i, param in enumerate(all_params)]
    new_params, new_kwonly_params, new_star_arg, new_star_kwarg = _restore_param_groups(formatted_params, node)
    params = Parameters(
        params=new_params,
        posonly_params=node.params.posonly_params,
        kwonly_params=new_kwonly_params,
        star_arg=new_star_arg if new_star_arg is not None else MaybeSentinel.DEFAULT,
        star_kwarg=new_star_kwarg,
    )
    whitespace_before_params = ParenthesizedWhitespace(
        last_line=SimpleWhitespace(' ' * indent_size),
        indent=True,
    )
    return params, whitespace_before_params
