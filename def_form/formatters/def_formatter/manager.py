import os
from collections.abc import Generator
from pathlib import Path

import tomli
import libcst as cst

from def_form.exceptions.base import BaseDefFormException
from def_form.formatters.def_formatter.checker import DefChecker
from def_form.formatters.def_formatter.formatter import DefFormatter
from def_form.utils.find_pyproject import find_pyproject_toml
from def_form.cli.ui import BaseUI


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
        ui: BaseUI | None = None,
    ) -> None:
        self.config: str = config or find_pyproject_toml()
        self.path = Path(path).resolve()
        self.ui = ui

        self.issues: list[BaseDefFormException] = []

        self.formatter_class = formatter
        self.checker_class = checker

        self._init_config(
            config=self.config,
            max_def_length=max_def_length,
            max_inline_args=max_inline_args,
            indent_size=indent_size,
        )

        self._init_exclusions(excluded or ())

        self.ui.show_config_info(
            config_path=self.config,
            max_inline_args=self.max_inline_args,
            max_def_length=self.max_def_length,
            indent_size=f'{self.indent_size} spaces',
            show_skipped=show_skipped,
            excluded=self.excluded,
        )

    # --------------------------------------------------------------------- #
    # Configuration
    # --------------------------------------------------------------------- #

    def _init_config(
        self,
        config: str,
        max_def_length: int | None,
        max_inline_args: int | None,
        indent_size: int | None,
    ) -> None:
        self.max_def_length = max_def_length
        self.max_inline_args = max_inline_args
        self.indent_size = indent_size

        self._config_excluded: list[str] = []

        if not config:
            return

        try:
            with Path(config).open("rb") as f:
                config_data = tomli.load(f)

            config_def = config_data.get("tool", {}).get("def-form", {})

            self.max_def_length = config_def.get(
                "max_def_length",
                self.max_def_length,
            )
            self.max_inline_args = config_def.get(
                "max_inline_args",
                self.max_inline_args,
            )
            self.indent_size = config_def.get(
                "indent_size",
                self.indent_size,
            )
            self._config_excluded = config_def.get("exclude", [])

        except (FileNotFoundError, tomli.TOMLDecodeError):
            self._config_excluded = []

    # --------------------------------------------------------------------- #
    # Exclusions
    # --------------------------------------------------------------------- #

    def _init_exclusions(self, cli_excluded: tuple[str, ...]) -> None:
        self.excluded: set[Path] = set()

        for p in (*cli_excluded, *self._config_excluded):
            try:
                self.excluded.add(Path(p).resolve())
            except Exception:
                continue

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

    # --------------------------------------------------------------------- #
    # File iteration
    # --------------------------------------------------------------------- #

    def _iter_py_files(self) -> Generator[Path, None, None]:
        if self.path.is_file():
            if self.path.suffix != ".py":
                return

            if self._is_excluded(self.path):
                self.ui.skipped(self.path)
                return

            yield self.path
            return

        for root, dirs, files in os.walk(self.path):
            root_path = Path(root)

            dirs[:] = [
                d for d in dirs if not self._is_excluded(root_path / d)
            ]

            for filename in files:
                if not filename.endswith(".py"):
                    continue

                file_path = root_path / filename

                if self._is_excluded(file_path):
                    self.ui.skipped(file_path)
                    continue

                yield file_path

    # --------------------------------------------------------------------- #
    # Processing
    # --------------------------------------------------------------------- #

    def _create_processor(
        self,
        processor_class: type[DefFormatter] | type[DefChecker],
        filepath: str,
    ) -> DefFormatter | DefChecker:
        return processor_class(
            filepath=filepath,
            max_def_length=self.max_def_length,
            max_inline_args=self.max_inline_args,
            indent_size=self.indent_size,
        )

    def _process_file(
        self,
        filepath: Path,
        processor_class: type[DefFormatter] | type[DefChecker],
    ) -> tuple[cst.Module | None, list[BaseDefFormException]]:
        try:
            code = filepath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None, []

        try:
            tree = cst.parse_module(code)
            wrapper = cst.metadata.MetadataWrapper(tree)
            processor = self._create_processor(processor_class, str(filepath))

            if issubclass(processor_class, DefFormatter):
                new_tree = wrapper.visit(processor)
                return new_tree, processor.issues

            wrapper.visit(processor)
            return None, processor.issues

        except cst.ParserSyntaxError:
            return None, []
        except Exception:
            return None, []

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #

    def format(self) -> None:
        self.issues.clear()
        files = list(self._iter_py_files())

        if self.ui:
            self.ui.start(total=len(files))

        for path in files:
            if self.ui:
                self.ui.processing(path)

            new_tree, file_issues = self._process_file(
                path,
                self.formatter_class,
            )

            self.issues.extend(file_issues)

            if new_tree is not None:
                try:
                    path.write_text(new_tree.code, encoding="utf-8")
                except OSError:
                    continue

        if self.ui:
            self.ui.finish(len(files), self.issues)

    def check(self) -> None:
        self.issues.clear()
        files = list(self._iter_py_files())

        if self.ui:
            self.ui.start(total=len(files))

        for path in files:
            if self.ui:
                self.ui.processing(path)

            _, file_issues = self._process_file(
                path,
                self.checker_class,
            )

            self.issues.extend(file_issues)

        if self.ui:
            self.ui.finish(len(files), self.issues)

        if self.issues:
            raise BaseDefFormException
