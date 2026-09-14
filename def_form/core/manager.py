import os
from collections.abc import Generator
from pathlib import Path
from typing import Any

import tomli
import libcst as cst

from def_form.cli.ui import BaseUI
from def_form.exceptions.base import BaseDefFormException
from def_form.exceptions.def_formatter import CheckCommandFoundAnIssue
from def_form.core.cache import DefCache
from def_form.core.checker import DefChecker
from def_form.core.formatter import DefFormatter
from def_form.core.models import CacheSignature
from def_form.core.models import ProcessResult
from def_form.utils.find_cache_root import find_cache_root
from def_form.utils.find_pyproject import find_pyproject_toml


class DefManager:
    def __init__(  # noqa: PLR0913
        self,
        path: str,
        ui: BaseUI,
        excluded: tuple[str, ...] | None = None,
        formatter: type[DefFormatter] = DefFormatter,
        checker: type[DefChecker] = DefChecker,
        max_def_length: int | None = None,
        max_inline_args: int | None = None,
        indent_size: int | None = None,
        config: str | None = None,
        show_skipped: bool = False,
        cache: bool | None = None,
    ) -> None:
        self.config: str | None = config or find_pyproject_toml()
        self.path: Path = Path(path).resolve()
        self.ui: BaseUI = ui
        self.show_skipped: bool = show_skipped

        self.issues: list[BaseDefFormException] = []

        self.formatter_class: type[DefFormatter] = formatter
        self.checker_class: type[DefChecker] = checker

        self._init_config(
            config=self.config,
            max_def_length=max_def_length,
            max_inline_args=max_inline_args,
            indent_size=indent_size,
            cache=cache,
        )

        self._init_exclusions(excluded or ())
        self._init_cache()

    def _show_config(self) -> None:
        self.ui.show_config_info(
            config_path=self.config,
            max_inline_args=self.max_inline_args,
            max_def_length=self.max_def_length,
            indent_size=f'{self.indent_size} spaces',
            show_skipped=self.show_skipped,
            cache=self.use_cache,
            excluded=self.excluded,
        )

    # --------------------------------------------------------------------- #
    # Configuration
    # --------------------------------------------------------------------- #

    def _read_config(self, config: str | None) -> dict[str, Any]:
        if not config:
            return {}

        try:
            with Path(config).open('rb') as f:
                config_data = tomli.load(f)
        except (OSError, tomli.TOMLDecodeError):
            return {}

        section = config_data.get('tool', {}).get('def-form', {})

        return section if isinstance(section, dict) else {}

    def _resolve_config_value(
        self,
        cli_value: Any,
        config_data: dict[str, Any],
        key: str,
        default: Any = None,
    ) -> Any:
        """A value given on the command line always wins over pyproject.toml"""
        if cli_value is not None:
            return cli_value

        return config_data.get(key, default)

    def _init_config(
        self,
        config: str | None,
        max_def_length: int | None,
        max_inline_args: int | None,
        indent_size: int | None,
        cache: bool | None,
    ) -> None:
        config_def = self._read_config(config)

        self.max_def_length: int | None = self._resolve_config_value(max_def_length, config_def, 'max_def_length')
        self.max_inline_args: int | None = self._resolve_config_value(max_inline_args, config_def, 'max_inline_args')
        self.indent_size: int | None = self._resolve_config_value(indent_size, config_def, 'indent_size')
        self.use_cache: bool = bool(self._resolve_config_value(cache, config_def, 'cache', default=True))

        config_excluded = config_def.get('exclude', [])
        self._config_excluded: list[str] = config_excluded if isinstance(config_excluded, list) else []

    # --------------------------------------------------------------------- #
    # Cache
    # --------------------------------------------------------------------- #

    def _build_cache_signature(self) -> CacheSignature | None:
        if not self.use_cache:
            return None

        return CacheSignature(
            tool_version=DefCache.tool_version(),
            max_def_length=self.max_def_length,
            max_inline_args=self.max_inline_args,
            indent_size=self.indent_size,
        )

    def _init_cache(self) -> None:
        self.cache: DefCache = DefCache(
            root=find_cache_root(),
            signature=self._build_cache_signature(),
            enabled=self.use_cache,
        )

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
            if self.path.suffix != '.py':
                return

            if self._is_excluded(self.path):
                self.ui.skipped(self.path)
                return

            yield self.path
            return

        for root, dirs, files in os.walk(self.path):
            root_path = Path(root)

            dirs[:] = [d for d in dirs if not self._is_excluded(root_path / d)]

            for filename in files:
                if not filename.endswith('.py'):
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

    def _read(self, filepath: Path) -> str | None:
        try:
            return filepath.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            return None

    def _process_code(
        self,
        code: str,
        filepath: Path,
        processor_class: type[DefFormatter] | type[DefChecker],
    ) -> ProcessResult:
        try:
            tree = cst.parse_module(code)
            wrapper = cst.metadata.MetadataWrapper(tree)
            processor = self._create_processor(processor_class, str(filepath))

            if issubclass(processor_class, DefFormatter):
                new_tree = wrapper.visit(processor)
                return ProcessResult(ok=True, module=new_tree, issues=processor.issues)

            wrapper.visit(processor)
            return ProcessResult(ok=True, issues=processor.issues)

        except cst.ParserSyntaxError:
            return ProcessResult(ok=False)
        except Exception:
            return ProcessResult(ok=False)

    def _process_file(
        self,
        filepath: Path,
        processor_class: type[DefFormatter] | type[DefChecker],
    ) -> tuple[cst.Module | None, list[BaseDefFormException]]:
        code: str | None = self._read(filepath)

        if code is None:
            return None, []

        result = self._process_code(code, filepath, processor_class)
        return result.module, result.issues

    def _load_source(self, path: Path) -> tuple[str, str] | None:
        """Returns the file content together with its digest, or None when it cannot be read."""
        code: str | None = self._read(path)

        if code is None:
            return None

        return code, DefCache.compute_digest(code)

    def _write(
        self,
        dest: str | Path,
        module: str,
    ) -> None:
        try:
            Path(dest).write_text(module, encoding='utf-8')
        except OSError:
            self.ui.console.error(f'Exception occurred while writing to {dest}')

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #

    def format(self) -> None:
        self._show_config()
        self.issues.clear()
        files = list(self._iter_py_files())

        self.ui.start(total=len(files))

        cached = 0

        for path in files:
            source = self._load_source(path)

            if source is not None and self.cache.is_fresh(path, source[1]):
                cached += 1
                self.ui.cached(path)
                continue

            self.ui.processing(path)

            if source is None:
                continue

            code, digest = source
            result = self._process_code(code, path, self.formatter_class)

            self.issues.extend(result.issues)

            if result.module is None:
                continue

            if result.module.code != code:
                self.cache.discard(path)
                self._write(
                    dest=path,
                    module=result.module.code,
                )
                continue

            if not result.issues:
                self.cache.store(path, digest)

        self.cache.save()
        self.ui.finish(len(files) - cached, self.issues, cached=cached)

    def check(self) -> None:
        self._show_config()
        self.issues.clear()
        files = list(self._iter_py_files())

        self.ui.start(total=len(files))

        cached = 0

        for path in files:
            source = self._load_source(path)

            if source is not None and self.cache.is_fresh(path, source[1]):
                cached += 1
                self.ui.cached(path)
                continue

            self.ui.processing(path)

            if source is None:
                continue

            code, digest = source
            result = self._process_code(code, path, self.checker_class)

            self.issues.extend(result.issues)

            if result.ok and not result.issues:
                self.cache.store(path, digest)
            else:
                self.cache.discard(path)

        self.cache.save()
        self.ui.finish(len(files) - cached, self.issues, cached=cached)

        if self.issues:
            raise CheckCommandFoundAnIssue(str(self.path), 'check command did found an issue')

    def clean(self) -> bool:
        """Drops the whole cache directory; False means there was nothing to remove"""
        return self.cache.clear()
