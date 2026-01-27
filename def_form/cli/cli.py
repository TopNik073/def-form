import sys

import click

from def_form.exceptions.base import BaseDefFormException
from def_form.formatters import DefManager


@click.command()
@click.argument('path', type=str, default='src')
@click.option('--max-def-length', type=int, default=None, help='max length of your function definition')
@click.option('--max-inline-args', type=int, default=None, help='max number of inline arguments')
@click.option('--indent-size', type=int, default=None, help='indent size in spaces (default: 4)')
@click.option('--config', type=str, default=None, help='path to pyproject.toml')
@click.option('--exclude', multiple=True, help='paths to exclude from formatting')
@click.option('--show-skipped', is_flag=True, help='show skipped files/directories')
def format(  # noqa: PLR0913
    path: str,
    max_def_length: int | None,
    max_inline_args: int | None,
    indent_size: int | None,
    config: str | None,
    exclude: tuple[str, ...],
    show_skipped: bool,
) -> None:
    click.echo('Start formatting your code')
    try:
        DefManager(
            path=path,
            excluded=exclude,
            max_def_length=max_def_length,
            max_inline_args=max_inline_args,
            indent_size=indent_size,
            config=config,
            show_skipped=show_skipped,
        ).format()
    except Exception as e:
        click.echo(f'Something went wrong: {e}', err=True)
        sys.exit(1)
    else:
        click.echo('Formatted!')


@click.command()
@click.argument('path', type=str, default='src')
@click.option('--max-def-length', type=int, default=None, help='max length of your function definition')
@click.option('--max-inline-args', type=int, default=None, help='max number of inline arguments')
@click.option('--indent-size', type=int, default=None, help='indent size in spaces (default: 4)')
@click.option('--config', type=str, default=None, help='path to pyproject.toml')
@click.option('--exclude', multiple=True, help='paths to exclude from checking')
@click.option('--show-skipped', is_flag=True, help='show skipped files/directories')
def check(  # noqa: PLR0913
    path: str,
    max_def_length: int | None,
    max_inline_args: int | None,
    indent_size: int | None,
    config: str | None,
    exclude: tuple[str, ...],
    show_skipped: bool,
) -> None:
    click.echo('Start checking your code')
    try:
        DefManager(
            path=path,
            excluded=exclude,
            max_def_length=max_def_length,
            max_inline_args=max_inline_args,
            indent_size=indent_size,
            config=config,
            show_skipped=show_skipped,
        ).check()
    except BaseDefFormException:
        sys.exit(1)
    except Exception as e:
        click.echo(f'Something went wrong: {e}', err=True)
        sys.exit(1)
    else:
        click.echo('All checks passed!')
