from dataclasses import dataclass


@dataclass
class CLIContext:
    verbose: bool = False
    quiet: bool = False
    show_skipped: bool = False
    config_path: str | None = None

    @property
    def should_output(self) -> bool:
        return not self.quiet


context: CLIContext = CLIContext()
