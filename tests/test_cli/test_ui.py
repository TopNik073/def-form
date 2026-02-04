from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from def_form.cli.context import CLIContext
from def_form.cli.console.base import BaseConsole
from def_form.cli.console.rich import RichConsole
from def_form.cli.ui.base import BaseUI
from def_form.cli.ui.null import NullUI
from def_form.cli.ui.rich import RichUI
from def_form.exceptions.base import BaseDefFormException
from def_form.exceptions.def_formatter import TooManyInlineArgumentsException


def _make_base_ui_console() -> MagicMock:
    ctx = CLIContext()
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    return console


def test_base_ui_abstract_methods_raise_not_implemented() -> None:
    class StubUI(BaseUI):
        def show_config_info(self, **kwargs: object) -> None:
            super().show_config_info(**kwargs)

        def start(self, total: int | None) -> None:
            super().start(total)

        def processing(self, path: Path) -> None:
            super().processing(path)

        def skipped(self, path: Path) -> None:
            super().skipped(path)

        def finish(self, processed: int, issues: list[BaseDefFormException]) -> None:
            super().finish(processed, issues)

        def show_issues(self, processed: int, issues: list[BaseDefFormException]) -> None:
            super().show_issues(processed, issues)

        def show_summary(self, processed: int, issues: list[BaseDefFormException]) -> None:
            super().show_summary(processed, issues)

    console = _make_base_ui_console()
    ui = StubUI(console=console)

    with pytest.raises(NotImplementedError):
        ui.show_config_info()
    with pytest.raises(NotImplementedError):
        ui.start(1)
    with pytest.raises(NotImplementedError):
        ui.processing(Path('x.py'))
    with pytest.raises(NotImplementedError):
        ui.skipped(Path('y'))
    with pytest.raises(NotImplementedError):
        ui.finish(1, [])
    with pytest.raises(NotImplementedError):
        ui.show_issues(1, [])
    with pytest.raises(NotImplementedError):
        ui.show_summary(1, [])


def test_null_ui_all_methods_no_op() -> None:
    ctx = CLIContext()
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = NullUI(console=console)
    ui.show_config_info()
    ui.start(1)
    ui.processing(Path('x.py'))
    ui.skipped(Path('y'))
    ui.finish(1, [])
    ui.show_issues(1, [])
    ui.show_summary(1, [])


def test_rich_ui_show_config_info_skips_when_quiet() -> None:
    ctx = CLIContext()
    ctx.quiet = True
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.show_config_info(config_path='x', max_def_length=100)
    console.print.assert_not_called()


def test_rich_ui_show_config_info_skips_when_empty_config() -> None:
    ctx = CLIContext()
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.show_config_info()
    console.print.assert_not_called()


def test_rich_ui_show_config_info_prints_table_when_output_on() -> None:
    ctx = CLIContext()
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.show_config_info(config_path='/cfg', max_def_length=100, max_inline_args=2)
    assert console.print.call_count >= 1


def test_rich_ui_start_skips_when_quiet() -> None:
    ctx = CLIContext()
    ctx.quiet = True
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.start(5)
    assert ui.progress is None


def test_rich_ui_processing_skips_when_quiet() -> None:
    ctx = CLIContext()
    ctx.quiet = True
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.processing(Path('a.py'))
    assert ui.current_file is None


def test_rich_ui_skipped_skips_when_show_skipped_false() -> None:
    ctx = CLIContext()
    ctx.show_skipped = False
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.skipped(Path('x'))
    console.print.assert_not_called()


def test_rich_ui_finish_skips_when_quiet() -> None:
    ctx = CLIContext()
    ctx.quiet = True
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.finish(0, [])


def test_rich_ui_show_issues_skips_when_quiet() -> None:
    ctx = CLIContext()
    ctx.quiet = True
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.show_issues(1, [TooManyInlineArgumentsException(path='f:1', message='m')])
    console.print.assert_not_called()


def test_rich_ui_show_issues_prints_when_issues_and_output_on() -> None:
    ctx = CLIContext()
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.show_issues(1, [TooManyInlineArgumentsException(path='f:1', message='msg')])
    assert console.print.call_count >= 1


def test_rich_ui_show_summary_skips_when_quiet() -> None:
    ctx = CLIContext()
    ctx.quiet = True
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.show_summary(1, [])
    console.print.assert_not_called()


def test_rich_ui_convert_to_string_path(tmp_path: Path) -> None:
    ctx = CLIContext()
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    with patch.object(Path, 'cwd', return_value=tmp_path):
        s = ui._convert_to_string(tmp_path / 'sub' / 'file.py')
    assert s == 'sub/file.py' or 'sub' in s


def test_rich_ui_convert_to_string_bool() -> None:
    ctx = CLIContext()
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    assert ui._convert_to_string(True) == 'Yes'
    assert ui._convert_to_string(False) == 'No'


def test_rich_ui_show_config_info_skips_none_and_empty_values() -> None:
    ctx = CLIContext()
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.show_config_info(config_path='/x', max_def_length=None, indent_size='')
    assert console.print.call_count >= 1


def test_rich_ui_show_config_info_config_path_bold_yellow() -> None:
    ctx = CLIContext()
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.show_config_info(config_path='/project/pyproject.toml')
    assert console.print.call_count >= 1


def test_rich_ui_show_config_info_list_value_more_than_three() -> None:
    ctx = CLIContext()
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.show_config_info(excluded=['a', 'b', 'c', 'd'])
    assert console.print.call_count >= 1


def test_rich_ui_start_creates_progress_when_output_on() -> None:
    ctx = CLIContext()
    console = RichConsole(context=ctx, file=StringIO())
    ui = RichUI(console=console)
    ui.start(10)
    assert ui.progress is not None
    assert ui._live is not None
    assert ui.task_id is not None


def test_rich_ui_processing_updates_display_when_started() -> None:
    ctx = CLIContext()
    console = RichConsole(context=ctx, file=StringIO())
    ui = RichUI(console=console)
    ui.start(5)
    ui.processing(Path('foo/bar.py'))
    assert ui.current_file == Path('foo/bar.py')
    assert ui._progress_display.renderables[0] is not None


def test_rich_ui_skipped_prints_when_show_skipped_true() -> None:
    ctx = CLIContext()
    ctx.show_skipped = True
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.skipped(Path('skipped.py'))
    console.print.assert_called_once()
    assert 'SKIPPED' in str(console.print.call_args[0][0])


def test_rich_ui_issue_no_op() -> None:
    ctx = CLIContext()
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.issue(TooManyInlineArgumentsException(path='f:1', message='m'))


def test_rich_ui_finish_stops_live_and_shows_issues_when_present() -> None:
    ctx = CLIContext()
    console = RichConsole(context=ctx, file=StringIO())
    ui = RichUI(console=console)
    ui.start(2)
    ui.finish(2, [TooManyInlineArgumentsException(path='f:1', message='err')])
    assert ui._live is None
    assert ui.progress is None


def test_rich_ui_show_issues_line_info_when_colon_in_path() -> None:
    ctx = CLIContext()
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.show_issues(1, [TooManyInlineArgumentsException(path='f.py:10', message='m')])
    assert console.print.call_count >= 1


def test_rich_ui_show_issues_line_info_when_issue_has_line() -> None:
    ctx = CLIContext()
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    exc = TooManyInlineArgumentsException(path='f.py', message='m')
    exc.line = 5
    ui.show_issues(1, [exc])
    assert console.print.call_count >= 1
    out = str(console.print.call_args_list)
    assert ':5' in out or '5' in out


def test_rich_ui_show_summary_success_rate_branches() -> None:
    ctx = CLIContext()
    console = MagicMock(spec=BaseConsole)
    console.context = ctx
    ui = RichUI(console=console)
    ui.show_summary(100, [TooManyInlineArgumentsException(path='a.py:1', message='x')])
    assert console.print.call_count >= 1
    ui.show_summary(10, [TooManyInlineArgumentsException(path=f'f{i}.py:1', message='x') for i in range(10)])
    assert console.print.call_count >= 2
