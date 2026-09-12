import click

from def_form.cli.console import RichConsole
from def_form.cli.context import context
from def_form.cli.errors import CleanFailedError
from def_form.cli.ui.rich import RichUI
from def_form.core import DefManager


@click.command()
def clean() -> None:
    console = RichConsole(context=context)

    try:
        manager = DefManager(path='.', cache=False, ui=RichUI(console=console))
        removed = manager.clean()
    except Exception as exc:
        raise CleanFailedError(str(exc)) from exc

    if not removed:
        console.info(f'No cache found at [bold]{manager.cache.dir}[/bold]')
        return

    console.success(f'Removed cache at {manager.cache.dir}')
