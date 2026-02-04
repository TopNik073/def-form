from click.testing import CliRunner

from def_form.cli.main import cli


runner = CliRunner()


def test_cli_help_exit_zero() -> None:
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'format' in result.output
    assert 'check' in result.output
    assert '--verbose' in result.output
    assert '--quiet' in result.output


def test_format_help_exit_zero() -> None:
    result = runner.invoke(cli, ['format', '--help'])
    assert result.exit_code == 0
    assert 'path' in result.output.lower()
    assert '--max-def-length' in result.output
    assert '--max-inline-args' in result.output
    assert '--indent-size' in result.output
    assert '--config' in result.output
    assert '--exclude' in result.output
    assert '--show-skipped' in result.output


def test_check_help_exit_zero() -> None:
    result = runner.invoke(cli, ['check', '--help'])
    assert result.exit_code == 0
    assert 'path' in result.output.lower()
    assert '--max-def-length' in result.output
    assert '--max-inline-args' in result.output
    assert '--config' in result.output
    assert '--exclude' in result.output


def test_cli_verbose_quiet_flags() -> None:
    result = runner.invoke(cli, ['--verbose', '--help'])
    assert result.exit_code == 0
    result = runner.invoke(cli, ['--quiet', '--help'])
    assert result.exit_code == 0
