import click

from def_form.cli.cli import check
from def_form.cli.cli import format


@click.group(name='def-form')
def main() -> None:
    click.help_option()


main.add_command(format)
main.add_command(check)

if __name__ == '__main__':
    main()
