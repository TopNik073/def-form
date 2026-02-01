from rich.console import Console as RichConsole

from def_form.cli.context import CLIContext


class Console(RichConsole):
    def __init__(self, context: CLIContext, *args, **kwargs) -> None:
        self.context = context
        super().__init__(*args, **kwargs)

    def info(self, message: str) -> None:
        if self.context.should_output:
            self.print(message)

    def success(self, message: str) -> None:
        if self.context.should_output:
            self.print(f"[green]{message}[/green]")

    def warning(self, message: str) -> None:
        self.print(f"[yellow]{message}[/yellow]")

    def error(self, message: str) -> None:
        self.print(f"[red]{message}[/red]")

    def debug(self, message: str) -> None:
        if self.context.verbose:
            self.print(f"[dim]{message}[/dim]")
