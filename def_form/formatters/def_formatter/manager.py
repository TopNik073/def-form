import os
import tomli
from collections.abc import Generator
from pathlib import Path

import click
import libcst as cst

from def_form.exceptions.base import BaseDefFormException
from def_form.formatters.def_formatter.checker import DefChecker
from def_form.formatters.def_formatter.formatter import DefFormatter
from def_form.utils.find_pyproject import find_pyproject_toml


class DefManager:
    def __init__(  # noqa: PLR0913
        self,
        path: str,
        excluded: tuple[str, ...] | None = None,
        formatter: type[DefFormatter] = DefFormatter,
        checker: type[DefChecker] = DefChecker,
        max_def_length: int | None = None,
        max_inline_args: int | None = None,
        indent_size: int | None = None,
        config: str | None = None,
        show_skipped: bool = False,
    ):
        self.path = Path(path).resolve()
        self.show_skipped = show_skipped
        self.issues: list[BaseDefFormException] = []

        self._init_config(
            config=config,
            max_def_length=max_def_length,
            max_inline_args=max_inline_args,
            indent_size=indent_size,
        )

        self._init_exclusions(excluded or ())

        self.formatter_class = formatter
        self.checker_class = checker

    def _init_config(
        self,
        config: str | None,
        max_def_length: int | None,
        max_inline_args: int | None,
        indent_size: int | None,
    ) -> None:
        self.max_def_length = max_def_length
        self.max_inline_args = max_inline_args
        self.indent_size = indent_size

        if not config:
            config = find_pyproject_toml()

        config_excluded: list[str] = []

        if config:
            try:
                with Path.open(Path(config), 'rb') as f:
                    click.secho(f'Using config: {config}', fg='yellow')
                    config_data = tomli.load(f)

                config_def = config_data.get('tool', {}).get('def-form', {})

                self.max_def_length = config_def.get(
                    'max_def_length',
                    self.max_def_length,
                )
                self.max_inline_args = config_def.get(
                    'max_inline_args',
                    self.max_inline_args,
                )

                self.indent_size = config_def.get(
                    'indent_size',
                    self.indent_size,
                )

                config_excluded = config_def.get('exclude', [])
            except (FileNotFoundError, tomli.TOMLDecodeError) as e:
                click.secho(f'Error loading config {config}: {e}', fg='red')
                self.is_config_found = False

        self._config_excluded = config_excluded

    def _init_exclusions(self, cli_excluded: tuple[str, ...]) -> None:
        self.excluded: set[Path] = set()

        for p in (*cli_excluded, *self._config_excluded):
            try:
                excluded_path = Path(p).resolve()
                self.excluded.add(excluded_path)
            except Exception:
                click.secho(f'Warning: invalid excluded path: {p}', fg='yellow')

    def _iter_py_files(self) -> Generator[str, None, None]:
        if self.path.is_file():
            if self.path.suffix != '.py':
                return

            if self._is_excluded(self.path):
                if self.show_skipped:
                    click.secho(f'SKIPPED {self.path}', fg='yellow')
                return

            click.secho(f'Processing: {self.path}', fg='green')
            yield str(self.path)
            return

        for root, dirs, files in os.walk(self.path):
            root_path = Path(root)

            dirs[:] = [d for d in dirs if not self._is_excluded(root_path / d)]

            for filename in files:
                if not filename.endswith('.py'):
                    continue

                file_path = root_path / filename

                if self._is_excluded(file_path):
                    if self.show_skipped:
                        click.secho(f'SKIPPED {file_path}', fg='yellow')
                    continue

                click.secho(f'Processing: {file_path}', fg='green')
                yield str(file_path)

    def _is_excluded(self, path: Path) -> bool:
        for excluded in self.excluded:
            try:
                path.relative_to(excluded)
                return True
            except ValueError:
                pass

            if excluded.name in path.parts:
                return True

        return False

    def _create_processor(
        self, processor_class: type[DefFormatter] | type[DefChecker], filepath: str
    ) -> DefFormatter | DefChecker:
        return processor_class(
            filepath=filepath,
            max_def_length=self.max_def_length,
            max_inline_args=self.max_inline_args,
            indent_size=self.indent_size,
        )

    def _process_file(
        self,
        filepath: str,
        processor_class: type[DefFormatter] | type[DefChecker],
    ) -> tuple[cst.Module | None, list[BaseDefFormException]]:
        try:
            with Path.open(Path(filepath), encoding='utf-8') as f:
                code = f.read()
        except (OSError, UnicodeDecodeError) as e:
            click.secho(f'Error reading {filepath}: {e}', fg='red')
            return None, []

        try:
            tree = cst.parse_module(code)
            wrapper = cst.metadata.MetadataWrapper(tree)
            processor = self._create_processor(processor_class, filepath)

            if issubclass(processor_class, DefFormatter):
                new_tree = wrapper.visit(processor)
                return new_tree, processor.issues
            wrapper.visit(processor)
            return None, processor.issues

        except cst.ParserSyntaxError as e:
            click.secho(f'Syntax error in {filepath}: {e}', fg='red')
            return None, []
        except Exception as e:
            click.secho(f'Unexpected error processing {filepath}: {e}', fg='red')
            return None, []

    def format(self, write_to: str | None = None) -> None:
        processed_count = 0
        self.issues.clear()

        for filepath in self._iter_py_files():
            processed_count += 1
            new_tree, file_issues = self._process_file(filepath, self.formatter_class)

            self.issues.extend(file_issues)

            if new_tree is not None:
                try:
                    with Path.open(Path(write_to or filepath), 'w', encoding='utf-8') as f:
                        f.write(new_tree.code)
                except OSError as e:
                    click.secho(f'Error writing {filepath}: {e}', fg='red')

        self._echo_summary('format', processed_count)

    def check(self) -> None:
        processed_count = 0
        self.issues.clear()

        for filepath in self._iter_py_files():
            processed_count += 1
            _, file_issues = self._process_file(filepath, self.checker_class)
            self.issues.extend(file_issues)

        self._echo_summary('check', processed_count)

        if self.issues:
            raise BaseDefFormException

    def _echo_summary(self, mode: str, processed_count: int) -> None:
        click.echo('\n')

        if self.issues:
            click.secho('Issues:', fg='yellow', bold=True)
            for i, issue in enumerate(self.issues, 1):
                click.secho(f'{issue.path}', color=True)
                click.secho(f'  {issue.message}', fg='white')
                if i != len(self.issues):
                    click.echo('')

        click.echo('')
        click.secho(f'{mode.capitalize()} Summary:', fg='cyan', bold=True)
        click.echo(f'Processed files: {processed_count}')
        click.echo(f'Issues found: {len(self.issues)}')
