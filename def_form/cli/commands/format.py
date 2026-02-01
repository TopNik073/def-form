import click

from def_form.cli.commands.options import common_options
from def_form.cli.console import RichConsole
from def_form.cli.context import context
from def_form.cli.errors import FormatterFailedError
from def_form.cli.ui.rich import RichUI
from def_form.core import DefManager


@click.command()
@common_options
def format(  # noqa: PLR0913
    path: str,
    max_def_length: int | None,
    max_inline_args: int | None,
    indent_size: int | None,
    config: str | None,
    exclude: tuple[str, ...],
    show_skipped: bool,
) -> None:
    context.show_skipped = show_skipped
    console = RichConsole(context=context)
    console.info(f'Formatting [bold]{path}[/bold]')
    console.debug('Initializing formatter')

    try:
        DefManager(
            path=path,
            excluded=exclude,
            max_def_length=max_def_length,
            max_inline_args=max_inline_args,
            indent_size=indent_size,
            config=config,
            show_skipped=show_skipped,
            ui=RichUI(console=console),
        ).format()
    except Exception as exc:
        raise FormatterFailedError(str(exc)) from exc

    console.success('Formatting completed')
