import click
import sys
from def_form.cli.console import Console
from def_form.cli.context import context
from def_form.cli.errors import CLIError
from def_form.cli.commands.check import check
from def_form.cli.commands.format import format

console = Console(context=context)

@click.group()
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.option('--quiet', is_flag=True, help='Disable all output')
def cli(verbose: bool, quiet: bool) -> None:
    console.context.verbose = verbose
    console.context.quiet = quiet


cli.add_command(check)
cli.add_command(format)


def main() -> None:
    try:
        cli()
    except CLIError as exc:
        console.error(str(exc))
        sys.exit(1)
    except KeyboardInterrupt:
        console.error("Operation cancelled by user")
        sys.exit(130)
    except Exception as exc:
        console.error(f"Unexpected error: {exc}")
        sys.exit(1)


if __name__ == '__main__':
    main()