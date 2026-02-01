import pytest
from unittest.mock import patch

from def_form.cli.main import main
from def_form.cli.errors import CLIError


def test_main_exits_1_on_cli_error() -> None:
    with patch('def_form.cli.main.cli', side_effect=CLIError('test error')):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1


def test_main_exits_130_on_keyboard_interrupt() -> None:
    with patch('def_form.cli.main.cli', side_effect=KeyboardInterrupt):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 130


def test_main_exits_1_on_generic_exception() -> None:
    with patch('def_form.cli.main.cli', side_effect=RuntimeError('unexpected')):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1
