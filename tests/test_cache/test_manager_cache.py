import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from def_form.cli.console import NullConsole
from def_form.cli.context import CLIContext
from def_form.cli.ui import NullUI
from def_form.core import DefManager
from def_form.core.cache import CACHE_DIR_NAME
from def_form.core.cache import MANIFEST_NAME
from def_form.exceptions.def_formatter import CheckCommandFoundAnIssue


CLEAN_CODE = 'def foo(a, b):\n    return a\n'
DIRTY_CODE = 'def bar(a, b, c, d):\n    return a\n'

PYPROJECT = """
[tool.def-form]
max_def_length = 100
max_inline_args = 2
indent_size = 4
"""


class CountingUI(NullUI):
    def __init__(self, console: NullConsole) -> None:
        super().__init__(console=console)
        self.processed: list[Path] = []
        self.cached_paths: list[Path] = []

    def processing(self, path: Path) -> None:
        self.processed.append(path)

    def cached(self, path: Path) -> None:
        self.cached_paths.append(path)


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / 'pyproject.toml').write_text(PYPROJECT, encoding='utf-8')
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _make_ui() -> CountingUI:
    return CountingUI(console=NullConsole(context=CLIContext()))


def _make_manager(project: Path, ui: CountingUI, **overrides: Any) -> DefManager:
    kwargs: dict[str, Any] = {
        'config': str(project / 'pyproject.toml'),
        'excluded': (),
        'path': str(project),
        'ui': ui,
    }
    kwargs.update(overrides)
    return DefManager(**kwargs)


def _cached_files(project: Path) -> dict[str, str]:
    path = project / CACHE_DIR_NAME / MANIFEST_NAME

    if not path.is_file():
        return {}

    return json.loads(path.read_text(encoding='utf-8'))['files']


def test_check_caches_clean_file(project: Path) -> None:
    (project / 'clean.py').write_text(CLEAN_CODE, encoding='utf-8')

    ui = _make_ui()
    _make_manager(project, ui).check()

    assert ui.processed == [project / 'clean.py']
    assert list(_cached_files(project)) == ['clean.py']


def test_second_check_skips_cached_file(project: Path) -> None:
    (project / 'clean.py').write_text(CLEAN_CODE, encoding='utf-8')

    _make_manager(project, _make_ui()).check()

    ui = _make_ui()
    _make_manager(project, ui).check()

    assert ui.processed == []
    assert ui.cached_paths == [project / 'clean.py']


def test_edited_file_is_rechecked(project: Path) -> None:
    target = project / 'clean.py'
    target.write_text(CLEAN_CODE, encoding='utf-8')

    _make_manager(project, _make_ui()).check()

    target.write_text(DIRTY_CODE, encoding='utf-8')

    ui = _make_ui()
    with pytest.raises(CheckCommandFoundAnIssue):
        _make_manager(project, ui).check()

    assert ui.processed == [target]
    assert _cached_files(project) == {}


def test_file_with_issues_is_not_cached(project: Path) -> None:
    (project / 'dirty.py').write_text(DIRTY_CODE, encoding='utf-8')

    with pytest.raises(CheckCommandFoundAnIssue):
        _make_manager(project, _make_ui()).check()

    assert _cached_files(project) == {}

    ui = _make_ui()
    with pytest.raises(CheckCommandFoundAnIssue):
        _make_manager(project, ui).check()

    assert ui.processed == [project / 'dirty.py']


def test_unparsable_file_is_not_cached(project: Path) -> None:
    (project / 'broken.py').write_text('def (:\n', encoding='utf-8')

    _make_manager(project, _make_ui()).check()

    assert _cached_files(project) == {}


def test_format_does_not_cache_rewritten_file(project: Path) -> None:
    target = project / 'dirty.py'
    target.write_text(DIRTY_CODE, encoding='utf-8')

    _make_manager(project, _make_ui()).format()

    assert target.read_text(encoding='utf-8') != DIRTY_CODE
    assert _cached_files(project) == {}

    ui = _make_ui()
    _make_manager(project, ui).format()

    assert ui.processed == [target]
    assert list(_cached_files(project)) == ['dirty.py']


def test_format_caches_untouched_clean_file(project: Path) -> None:
    (project / 'clean.py').write_text(CLEAN_CODE, encoding='utf-8')

    _make_manager(project, _make_ui()).format()

    assert list(_cached_files(project)) == ['clean.py']

    ui = _make_ui()
    _make_manager(project, ui).format()

    assert ui.cached_paths == [project / 'clean.py']


def test_cache_disabled_writes_nothing(project: Path) -> None:
    (project / 'clean.py').write_text(CLEAN_CODE, encoding='utf-8')

    _make_manager(project, _make_ui(), cache=False).check()

    assert not (project / CACHE_DIR_NAME).exists()


def test_cache_disabled_via_pyproject(project: Path) -> None:
    (project / 'pyproject.toml').write_text(f'{PYPROJECT}cache = false\n', encoding='utf-8')
    (project / 'clean.py').write_text(CLEAN_CODE, encoding='utf-8')

    _make_manager(project, _make_ui()).check()

    assert not (project / CACHE_DIR_NAME).exists()


def test_cli_flag_wins_over_enabled_config(project: Path) -> None:
    (project / 'clean.py').write_text(CLEAN_CODE, encoding='utf-8')

    manager = _make_manager(project, _make_ui(), cache=False)

    assert manager.use_cache is False


def test_changed_settings_invalidate_cache(project: Path) -> None:
    (project / 'clean.py').write_text(CLEAN_CODE, encoding='utf-8')

    _make_manager(project, _make_ui()).check()

    (project / 'pyproject.toml').write_text(
        PYPROJECT.replace('max_inline_args = 2', 'max_inline_args = 1'),
        encoding='utf-8',
    )

    ui = _make_ui()
    with pytest.raises(CheckCommandFoundAnIssue):
        _make_manager(project, ui).check()

    assert ui.processed == [project / 'clean.py']


def test_deleted_file_is_pruned_from_manifest(project: Path) -> None:
    target = project / 'clean.py'
    target.write_text(CLEAN_CODE, encoding='utf-8')
    (project / 'other.py').write_text(CLEAN_CODE.replace('foo', 'baz'), encoding='utf-8')

    _make_manager(project, _make_ui()).check()
    assert len(_cached_files(project)) == 2

    target.unlink()
    _make_manager(project, _make_ui()).check()

    assert list(_cached_files(project)) == ['other.py']


def test_clean_removes_the_cache_directory(project: Path) -> None:
    (project / 'clean.py').write_text(CLEAN_CODE, encoding='utf-8')

    _make_manager(project, _make_ui()).check()
    assert (project / CACHE_DIR_NAME).is_dir()

    assert _make_manager(project, _make_ui()).clean() is True
    assert not (project / CACHE_DIR_NAME).exists()


def test_clean_returns_false_without_cache(project: Path) -> None:
    assert _make_manager(project, _make_ui()).clean() is False


def test_clean_works_with_cache_disabled(project: Path) -> None:
    (project / 'clean.py').write_text(CLEAN_CODE, encoding='utf-8')
    _make_manager(project, _make_ui()).check()

    assert _make_manager(project, _make_ui(), cache=False).clean() is True
    assert not (project / CACHE_DIR_NAME).exists()


def test_check_re_caches_after_clean(project: Path) -> None:
    (project / 'clean.py').write_text(CLEAN_CODE, encoding='utf-8')

    _make_manager(project, _make_ui()).check()
    _make_manager(project, _make_ui()).clean()

    ui = _make_ui()
    _make_manager(project, ui).check()

    assert ui.processed == [project / 'clean.py']
    assert list(_cached_files(project)) == ['clean.py']


def test_disabled_cache_does_not_look_up_the_tool_version(project: Path) -> None:
    from importlib.metadata import PackageNotFoundError

    (project / 'clean.py').write_text(CLEAN_CODE, encoding='utf-8')

    with patch('def_form.core.cache.package_version', side_effect=PackageNotFoundError):
        _make_manager(project, _make_ui(), cache=False).check()

    assert not (project / CACHE_DIR_NAME).exists()


def test_clean_works_without_the_tool_version(project: Path) -> None:
    from importlib.metadata import PackageNotFoundError

    (project / 'clean.py').write_text(CLEAN_CODE, encoding='utf-8')
    _make_manager(project, _make_ui()).check()

    with patch('def_form.core.cache.package_version', side_effect=PackageNotFoundError):
        assert _make_manager(project, _make_ui(), cache=False).clean() is True

    assert not (project / CACHE_DIR_NAME).exists()


def test_enabled_cache_still_requires_the_tool_version(project: Path) -> None:
    from importlib.metadata import PackageNotFoundError

    from def_form.exceptions.cache import ToolVersionNotFoundException

    (project / 'clean.py').write_text(CLEAN_CODE, encoding='utf-8')

    with patch('def_form.core.cache.package_version', side_effect=PackageNotFoundError):
        with pytest.raises(ToolVersionNotFoundException):
            _make_manager(project, _make_ui())
