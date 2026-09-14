from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
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


def test_format_passes_cache_none_by_default(tmp_path: Path) -> None:
    with patch('def_form.cli.commands.format.DefManager') as mock_manager_class:
        mock_manager_class.return_value = MagicMock()

        result = runner.invoke(cli, ['format', str(tmp_path)])

        assert result.exit_code == 0
        assert mock_manager_class.call_args[1]['cache'] is None


def test_format_no_cache_flag_disables_cache(tmp_path: Path) -> None:
    with patch('def_form.cli.commands.format.DefManager') as mock_manager_class:
        mock_manager_class.return_value = MagicMock()

        result = runner.invoke(cli, ['format', str(tmp_path), '--no-cache'])

        assert result.exit_code == 0
        assert mock_manager_class.call_args[1]['cache'] is False


def test_check_no_cache_flag_disables_cache(tmp_path: Path) -> None:
    with patch('def_form.cli.commands.check.DefManager') as mock_manager_class:
        mock_manager_class.return_value = MagicMock()

        result = runner.invoke(cli, ['check', str(tmp_path), '--no-cache'])

        assert result.exit_code == 0
        assert mock_manager_class.call_args[1]['cache'] is False


def test_clean_invokes_def_manager_clean(tmp_path: Path) -> None:
    with patch('def_form.cli.commands.clean.DefManager') as mock_manager_class:
        mock_instance = MagicMock()
        mock_instance.clean.return_value = True
        mock_manager_class.return_value = mock_instance

        result = runner.invoke(cli, ['clean'])

        assert result.exit_code == 0
        mock_instance.clean.assert_called_once()
        assert mock_manager_class.call_args[1]['path'] == '.'


def test_clean_raises_cli_error_on_exception() -> None:
    with patch('def_form.cli.commands.clean.DefManager') as mock_manager_class:
        mock_instance = MagicMock()
        mock_instance.clean.side_effect = OSError('permission denied')
        mock_manager_class.return_value = mock_instance

        result = runner.invoke(cli, ['clean'])

        assert result.exit_code != 0
        assert result.exc_info is not None
        from def_form.cli.errors import CleanFailedError
        assert isinstance(result.exc_info[1], CleanFailedError)


def test_clean_removes_existing_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from def_form.core.cache import CACHE_DIR_NAME

    (tmp_path / 'pyproject.toml').write_text('[tool.def-form]\n', encoding='utf-8')
    cache_dir = tmp_path / CACHE_DIR_NAME
    cache_dir.mkdir()
    (cache_dir / 'manifest.json').write_text('{}', encoding='utf-8')
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(cli, ['clean'])

    assert result.exit_code == 0
    assert not cache_dir.exists()


def test_clean_reports_missing_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / 'pyproject.toml').write_text('[tool.def-form]\n', encoding='utf-8')
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(cli, ['clean'])

    assert result.exit_code == 0


def test_check_reports_missing_tool_version(tmp_path: Path) -> None:
    from importlib.metadata import PackageNotFoundError

    from def_form.cli.errors import CheckFailedError

    with patch('def_form.core.cache.package_version', side_effect=PackageNotFoundError):
        result = runner.invoke(cli, ['check', str(tmp_path)])

    assert result.exit_code != 0
    assert result.exc_info is not None
    assert isinstance(result.exc_info[1], CheckFailedError)
    assert 'def-form version' in str(result.exc_info[1])


def test_clean_works_without_package_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from importlib.metadata import PackageNotFoundError

    from def_form.core.cache import CACHE_DIR_NAME

    (tmp_path / 'pyproject.toml').write_text('[tool.def-form]\n', encoding='utf-8')
    (tmp_path / CACHE_DIR_NAME).mkdir()
    monkeypatch.chdir(tmp_path)

    with patch('def_form.core.cache.package_version', side_effect=PackageNotFoundError):
        result = runner.invoke(cli, ['clean'])

    assert result.exit_code == 0
    assert not (tmp_path / CACHE_DIR_NAME).exists()
