# ruff: noqa: PLR2004
from collections import defaultdict
from pathlib import Path
from typing import Any

from rich import box
from rich.console import Group
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TaskID
from rich.table import Table
from rich.text import Text

from def_form.cli.console import BaseConsole
from def_form.cli.ui.base import BaseUI
from def_form.exceptions.base import BaseDefFormException


class RichUI(BaseUI):
    def __init__(self, console: BaseConsole) -> None:
        super().__init__(
            console=console,
        )
        self.progress: Progress | None = None
        self._live: Live | None = None
        self.task_id: int | None = None
        self.current_file: Path | None = None

    def _convert_to_string(self, value: Any) -> str:
        if isinstance(value, Path):
            return str(value.relative_to(Path.cwd()))

        if isinstance(value, bool):
            return 'Yes' if value else 'No'

        return str(value)

    def show_config_info(self, **config: Any) -> None:
        if not self.context.should_output:
            return

        if not config:
            return

        config_table = Table(
            title='[yellow]Configuration[/yellow]', box=box.HORIZONTALS, show_header=False, border_style='dim'
        )
        config_table.add_column(style='dim')
        config_table.add_column(style='cyan')

        for key, value in config.items():
            if value is None or value == '':
                continue

            display_key = key.replace('_', ' ').title()

            if key == 'config_path':
                config_table.add_row(f'{display_key}:', f'[bold yellow]{value}[/bold yellow]')
            else:
                if isinstance(value, list | set | tuple):
                    if not value:
                        continue

                    items = [self._convert_to_string(item) for item in value]

                    if len(items) <= 3:
                        display_value = ', '.join(items)
                    else:
                        preview = ', '.join(items[:3])
                        display_value = f'{preview} (+{len(items) - 3} more)'
                else:
                    display_value = self._convert_to_string(value)

                config_table.add_row(f'{display_key}:', display_value)

        self.console.print()
        self.console.print(config_table)
        self.console.print()

    def start(self, total: int | None) -> None:
        if not self.context.should_output:
            return

        self.progress = Progress(
            SpinnerColumn(),
            BarColumn(bar_width=None, complete_style='blue', finished_style='green'),
            TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
            TextColumn('•'),
            TimeElapsedColumn(),
            TextColumn('•'),
            TextColumn('{task.completed}/{task.total}'),
            console=self.console,
            expand=True,
        )

        self._progress_display = Group(Text('', style='dim'), self.progress)

        self._live = Live(self._progress_display, console=self.console, refresh_per_second=10)
        self._live.start()

        self.task_id = self.progress.add_task(
            'Processing files...',
            total=total,
        )

    def processing(self, path: Path) -> None:
        if not self.context.should_output:
            return

        if not (self.progress and self._live and self.task_id is not None):
            return

        self.current_file = path

        file_text = Text(str(path), style='dim')
        self._progress_display.renderables[0] = file_text

        self.progress.update(
            TaskID(self.task_id),
            advance=1,
        )

        self._live.refresh()

    def skipped(self, path: Path) -> None:
        if not self.context.should_output:
            return

        if not self.context.show_skipped:
            return

        self.console.print(f'[yellow]SKIPPED[/yellow] {path}')

    def issue(self, issue: BaseDefFormException) -> None:
        pass

    def finish(self, processed: int, issues: list[BaseDefFormException]) -> None:
        if not self.context.should_output:
            return

        if self._live:
            self._live.stop()
            self._live = None

        if self.progress:
            self.progress.stop()
            self.progress = None

        if issues:
            self.show_issues(processed, issues)

    def show_issues(self, processed: int, issues: list[BaseDefFormException]) -> None:
        if not self.context.should_output:
            return

        unique_files = {issue.path.split(':')[0] for issue in issues}

        if issues:
            self.console.print('\n')

            self.console.print(f'[bold yellow]Found {len(issues)} errors in {len(unique_files)} files[/bold yellow]')
            self.console.print()

            issues_by_def: dict[str, list[BaseDefFormException]] = defaultdict(list)
            for issue in issues:
                if issue.path not in issues_by_def:
                    issues_by_def[issue.path] = []
                issues_by_def[issue.path].append(issue)

            for i, (def_path, def_issues) in enumerate(sorted(issues_by_def.items())):
                if i > 0:
                    self.console.print()

                self.console.print(f'[bold cyan link=file://{def_path}]{def_path}[/bold cyan link=file://{def_path}]')

                for _j, issue in enumerate(def_issues):
                    bullet = '•'

                    line_info = ''
                    if ':' in def_path:
                        line_info = ''
                    elif hasattr(issue, 'line') and issue.line:
                        line_info = f':{issue.line}'

                    self.console.print(f'  [red]{bullet}[/red] [white]{issue.message}[/white]{line_info}')

            self.console.print()

        self.show_summary(processed, issues)

    def show_summary(self, processed: int, issues: list[BaseDefFormException]) -> None:
        if not self.context.should_output:
            return

        unique_files = {issue.path.split(':')[0] for issue in issues}

        summary = Table(title='[yellow]Summary[/yellow]', box=box.HORIZONTALS, show_header=False, border_style='dim')
        summary.add_column(style='bold')
        summary.add_column()

        summary.add_row('Files processed:', f'[cyan]{processed}[/cyan]')
        summary.add_row('Files with issues:', f'[yellow]{len(unique_files)}[/yellow]')
        summary.add_row('Total errors:', f'[red]{len(issues)}[/red]')

        if processed > 0:
            success_rate = (processed - len(unique_files)) / processed * 100
            summary.add_row(
                'Success rate:',
                f'[{"green" if success_rate > 90 else "yellow" if success_rate > 70 else "red"}]'
                f'{success_rate:.1f}%'
                f'[/{"green" if success_rate > 90 else "yellow" if success_rate > 70 else "red"}]',
            )

        self.console.print(summary)
        self.console.print()
