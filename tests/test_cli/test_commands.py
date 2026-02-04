from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

from click.testing import CliRunner

from def_form.cli.main import cli


runner = CliRunner()


def test_format_default_path_is_current_dir() -> None:
    with patch('def_form.cli.commands.format.DefManager') as mock_manager_class:
        mock_instance = MagicMock()
        mock_manager_class.return_value = mock_instance

        result = runner.invoke(cli, ['format'])

        assert result.exit_code == 0
        call_kw = mock_manager_class.call_args[1]
        assert call_kw['path'] == '.'


def test_format_invokes_def_manager_and_format(tmp_path: Path) -> None:
    with patch('def_form.cli.commands.format.DefManager') as mock_manager_class:
        mock_instance = MagicMock()
        mock_manager_class.return_value = mock_instance

        result = runner.invoke(cli, ['format', str(tmp_path)])

        assert result.exit_code == 0
        mock_manager_class.assert_called_once()
        call_kw = mock_manager_class.call_args[1]
        assert call_kw['path'] == str(tmp_path)
        assert call_kw['excluded'] == ()
        assert call_kw['max_def_length'] is None
        assert call_kw['max_inline_args'] is None
        assert call_kw['indent_size'] is None
        assert call_kw['config'] is None
        assert call_kw['show_skipped'] is False
        assert 'ui' in call_kw
        mock_instance.format.assert_called_once()


def test_format_passes_options_to_def_manager(tmp_path: Path) -> None:
    with patch('def_form.cli.commands.format.DefManager') as mock_manager_class:
        mock_instance = MagicMock()
        mock_manager_class.return_value = mock_instance

        result = runner.invoke(
            cli,
            [
                'format',
                str(tmp_path),
                '--max-def-length', '88',
                '--max-inline-args', '3',
                '--indent-size', '2',
                '--exclude', 'foo',
                '--exclude', 'bar',
                '--show-skipped',
            ],
        )

        assert result.exit_code == 0
        call_kw = mock_manager_class.call_args[1]
        assert call_kw['max_def_length'] == 88
        assert call_kw['max_inline_args'] == 3
        assert call_kw['indent_size'] == 2
        assert call_kw['excluded'] == ('foo', 'bar')
        assert call_kw['show_skipped'] is True


def test_check_invokes_def_manager_and_check(tmp_path: Path) -> None:
    with patch('def_form.cli.commands.check.DefManager') as mock_manager_class:
        mock_instance = MagicMock()
        mock_manager_class.return_value = mock_instance

        result = runner.invoke(cli, ['check', str(tmp_path)])

        assert result.exit_code == 0
        mock_manager_class.assert_called_once()
        call_kw = mock_manager_class.call_args[1]
        assert call_kw['path'] == str(tmp_path)
        assert call_kw['excluded'] == ()
        mock_instance.check.assert_called_once()


def test_check_passes_options_to_def_manager(tmp_path: Path) -> None:
    with patch('def_form.cli.commands.check.DefManager') as mock_manager_class:
        mock_instance = MagicMock()
        mock_manager_class.return_value = mock_instance

        result = runner.invoke(
            cli,
            [
                'check',
                str(tmp_path),
                '--max-def-length', '100',
                '--max-inline-args', '2',
                '--exclude', 'build',
            ],
        )

        assert result.exit_code == 0
        call_kw = mock_manager_class.call_args[1]
        assert call_kw['max_def_length'] == 100
        assert call_kw['max_inline_args'] == 2
        assert call_kw['excluded'] == ('build',)


def test_format_raises_cli_error_on_exception(tmp_path: Path) -> None:
    with patch('def_form.cli.commands.format.DefManager') as mock_manager_class:
        mock_instance = MagicMock()
        mock_instance.format.side_effect = RuntimeError('formatter broke')
        mock_manager_class.return_value = mock_instance

        result = runner.invoke(cli, ['format', str(tmp_path)])

        assert result.exit_code != 0
        assert result.exc_info is not None
        from def_form.cli.errors import FormatterFailedError
        assert isinstance(result.exc_info[1], FormatterFailedError)


def test_check_raises_cli_error_on_generic_exception(tmp_path: Path) -> None:
    with patch('def_form.cli.commands.check.DefManager') as mock_manager_class:
        mock_instance = MagicMock()
        mock_instance.check.side_effect = RuntimeError('something broke')
        mock_manager_class.return_value = mock_instance

        result = runner.invoke(cli, ['check', str(tmp_path)])

        assert result.exit_code != 0
        assert result.exc_info is not None
        from def_form.cli.errors import CheckFailedError
        assert isinstance(result.exc_info[1], CheckFailedError)
        assert 'something broke' in str(result.exc_info[1])


def test_check_raises_cli_error_on_base_def_form_exception(tmp_path: Path) -> None:
    from def_form.exceptions.def_formatter import TooManyInlineArgumentsException

    with patch('def_form.cli.commands.check.DefManager') as mock_manager_class:
        mock_instance = MagicMock()
        mock_instance.check.side_effect = TooManyInlineArgumentsException(
            path='file.py:1', message='too many args'
        )
        mock_manager_class.return_value = mock_instance

        result = runner.invoke(cli, ['check', str(tmp_path)])

        assert result.exit_code != 0
        assert result.exc_info is not None
        from def_form.cli.errors import CheckFailedError
        assert isinstance(result.exc_info[1], CheckFailedError)
