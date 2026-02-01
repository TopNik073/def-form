from unittest.mock import MagicMock

import pytest

from def_form.cli.context import CLIContext
from def_form.cli.console.base import BaseConsole
from def_form.cli.console.null import NullConsole
from def_form.cli.console.rich import RichConsole


def test_base_console_info_raises_not_implemented() -> None:
    ctx = CLIContext()
    console = BaseConsole(context=ctx)
    with pytest.raises(NotImplementedError):
        console.info('x')


def test_base_console_success_raises_not_implemented() -> None:
    ctx = CLIContext()
    console = BaseConsole(context=ctx)
    with pytest.raises(NotImplementedError):
        console.success('x')


def test_base_console_warning_raises_not_implemented() -> None:
    ctx = CLIContext()
    console = BaseConsole(context=ctx)
    with pytest.raises(NotImplementedError):
        console.warning('x')


def test_base_console_error_raises_not_implemented() -> None:
    ctx = CLIContext()
    console = BaseConsole(context=ctx)
    with pytest.raises(NotImplementedError):
        console.error('x')


def test_base_console_debug_raises_not_implemented() -> None:
    ctx = CLIContext()
    console = BaseConsole(context=ctx)
    with pytest.raises(NotImplementedError):
        console.debug('x')


def test_null_console_all_methods_no_op() -> None:
    ctx = CLIContext()
    console = NullConsole(context=ctx)
    console.info('x')
    console.success('x')
    console.warning('x')
    console.error('x')
    console.debug('x')


def test_rich_console_info_respects_should_output() -> None:
    ctx = CLIContext()
    ctx.quiet = True
    console = RichConsole(context=ctx)
    console.print = MagicMock()
    console.info('hi')
    console.print.assert_not_called()
    ctx.quiet = False
    console.info('hi')
    console.print.assert_called_once_with('hi')


def test_rich_console_success_respects_should_output() -> None:
    ctx = CLIContext()
    console = RichConsole(context=ctx)
    console.print = MagicMock()
    console.success('ok')
    console.print.assert_called_once()
    assert '[green]' in str(console.print.call_args[0][0])


def test_rich_console_warning_error_always_print() -> None:
    ctx = CLIContext()
    console = RichConsole(context=ctx)
    console.print = MagicMock()
    console.warning('w')
    console.print.assert_called_once()
    console.error('e')
    assert console.print.call_count == 2


def test_rich_console_debug_only_when_verbose() -> None:
    ctx = CLIContext()
    ctx.verbose = False
    console = RichConsole(context=ctx)
    console.print = MagicMock()
    console.debug('d')
    console.print.assert_not_called()
    ctx.verbose = True
    console.debug('d')
    console.print.assert_called_once()
