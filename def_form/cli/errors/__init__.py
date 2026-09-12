class CLIError(Exception):
    pass


class FormatterFailedError(CLIError):
    pass


class CheckFailedError(CLIError):
    pass


class CleanFailedError(CLIError):
    pass
