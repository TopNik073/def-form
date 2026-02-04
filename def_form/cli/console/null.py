from def_form.cli.console.base import BaseConsole


class NullConsole(BaseConsole):
    def info(self, message: str) -> None:
        return

    def success(self, message: str) -> None:
        return

    def warning(self, message: str) -> None:
        return

    def error(self, message: str) -> None:
        return

    def debug(self, message: str) -> None:
        return
