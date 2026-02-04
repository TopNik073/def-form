from collections.abc import Callable

import click


def path_option(func: Callable) -> Callable:
    return click.argument('path', type=click.Path(exists=True), default='.')(func)


def max_def_length_option(func: Callable) -> Callable:
    return click.option('--max-def-length', type=int, default=None, help='Maximum length of function definition')(func)


def max_inline_args_option(func: Callable) -> Callable:
    return click.option('--max-inline-args', type=int, default=None, help='Maximum number of inline arguments')(func)


def indent_size_option(func: Callable) -> Callable:
    return click.option('--indent-size', type=int, default=None, help='Indent size in spaces (default: 4)')(func)


def config_option(func: Callable) -> Callable:
    return click.option(
        '--config',
        type=click.Path(exists=True, dir_okay=False),
        default=None,
        help='Path to pyproject.toml configuration file',
    )(func)


def exclude_option(func: Callable) -> Callable:
    return click.option('--exclude', multiple=True, type=click.Path(), help='Paths to exclude from processing')(func)


def show_skipped_option(func: Callable) -> Callable:
    return click.option('--show-skipped', is_flag=True, default=False, help='Show skipped files and directories')(func)


def common_options(func: Callable) -> Callable:
    func = path_option(func)
    func = max_def_length_option(func)
    func = max_inline_args_option(func)
    func = indent_size_option(func)
    func = exclude_option(func)
    func = show_skipped_option(func)
    return config_option(func)
