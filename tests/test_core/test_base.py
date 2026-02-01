from pathlib import Path
from unittest.mock import patch

import libcst as cst

from def_form.core.base import DefBase
from def_form.core.checker import DefChecker


def _parse_and_get_function(code: str) -> cst.FunctionDef:
    tree = cst.parse_module(code)
    for node in tree.body:
        if isinstance(node, cst.FunctionDef):
            return node
    raise AssertionError('No FunctionDef in code')


def test_is_single_line_function_returns_false_when_def_line_has_no_paren_colon() -> None:
    code = 'def f(\n    x,\n):\n    pass\n'
    node = _parse_and_get_function(code)
    base = DefBase(filepath='x.py', max_def_length=None, max_inline_args=None)
    result = base.is_single_line_function(node)
    assert result is False


def test_has_skip_comment_returns_false_on_file_open_error(tmp_path: Path) -> None:
    py_file = tmp_path / 'f.py'
    py_file.write_text('def f(): pass\n', encoding='utf-8')
    code = py_file.read_text()
    tree = cst.parse_module(code)
    wrapper = cst.metadata.MetadataWrapper(tree)
    checker = DefChecker(
        filepath=str(py_file),
        max_def_length=None,
        max_inline_args=None,
        indent_size=4,
    )

    def open_side_effect(self: Path, *args: object, **kwargs: object) -> object:
        if str(self) == str(py_file):
            raise OSError('permission denied')
        return Path.open(self, *args, **kwargs)

    with patch.object(Path, 'open', open_side_effect):
        wrapper.visit(checker)
    assert checker.issues == []


def test_has_skip_comment_returns_false_on_unicode_decode_error(tmp_path: Path) -> None:
    py_file = tmp_path / 'f.py'
    py_file.write_text('def f(): pass\n', encoding='utf-8')
    tree = cst.parse_module(py_file.read_text())
    wrapper = cst.metadata.MetadataWrapper(tree)
    checker = DefChecker(
        filepath=str(py_file),
        max_def_length=None,
        max_inline_args=None,
        indent_size=4,
    )

    def open_side_effect(self: Path, *args: object, **kwargs: object) -> object:
        if str(self) == str(py_file):
            raise UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')
        return Path.open(self, *args, **kwargs)

    with patch.object(Path, 'open', open_side_effect):
        wrapper.visit(checker)
    assert checker.issues == []


def test_has_correct_multiline_params_format_false_when_not_parenthesized_whitespace() -> None:
    code = 'def f(x): pass\n'
    node = _parse_and_get_function(code)
    base = DefBase(filepath='x.py', max_def_length=None, max_inline_args=None)
    result = base.has_correct_multiline_params_format(node)
    assert result is False


def test_count_arguments_includes_star_arg() -> None:
    code = 'def f(a, *args): pass\n'
    node = _parse_and_get_function(code)
    base = DefBase(filepath='x.py', max_def_length=None, max_inline_args=None)
    count = base._count_arguments(node)
    assert count == 2


def test_count_arguments_includes_star_kwarg() -> None:
    code = 'def f(a, **kwargs): pass\n'
    node = _parse_and_get_function(code)
    base = DefBase(filepath='x.py', max_def_length=None, max_inline_args=None)
    count = base._count_arguments(node)
    assert count == 2
