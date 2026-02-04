from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

from def_form.cli.context import CLIContext
from def_form.cli.console.null import NullConsole
from def_form.cli.ui.null import NullUI
from def_form.core.manager import DefManager


def _make_manager(path: str = '.', config: str | None = None, excluded: tuple[str, ...] = ()) -> DefManager:
    ctx = CLIContext()
    ui = NullUI(console=NullConsole(context=ctx))
    return DefManager(path=path, ui=ui, config=config, excluded=excluded or ())


def test_init_config_with_no_config_keeps_defaults(tmp_path: Path) -> None:
    with patch('def_form.core.manager.find_pyproject_toml', return_value=None):
        m = _make_manager(path=str(tmp_path), config=None)
    assert m.max_def_length is None
    assert m.max_inline_args is None
    assert m.indent_size is None
    assert m._config_excluded == []


def test_init_config_loads_from_pyproject(tmp_path: Path) -> None:
    pyproject = tmp_path / 'pyproject.toml'
    pyproject.write_text(
        '[tool.def-form]\n'
        'max_def_length = 88\n'
        'max_inline_args = 3\n'
        'indent_size = 2\n'
        'exclude = ["venv", "build"]\n',
        encoding='utf-8',
    )
    with patch('def_form.core.manager.find_pyproject_toml', return_value=None):
        m = _make_manager(path=str(tmp_path), config=str(pyproject))
    assert m.max_def_length == 88
    assert m.max_inline_args == 3
    assert m.indent_size == 2
    assert m._config_excluded == ['venv', 'build']


def test_init_config_with_missing_file_sets_excluded_empty(tmp_path: Path) -> None:
    with patch('def_form.core.manager.find_pyproject_toml', return_value=None):
        m = _make_manager(path=str(tmp_path), config='/nonexistent/pyproject.toml')
    assert m._config_excluded == []


def test_init_exclusions_adds_resolved_paths(tmp_path: Path) -> None:
    sub = tmp_path / 'sub'
    sub.mkdir(exist_ok=True)
    with patch('def_form.core.manager.find_pyproject_toml', return_value=None):
        m = _make_manager(path=str(tmp_path), config=None, excluded=(str(sub),))
    assert len(m.excluded) >= 1


def test_is_excluded_true_when_path_under_excluded(tmp_path: Path) -> None:
    with patch('def_form.core.manager.find_pyproject_toml', return_value=None):
        m = _make_manager(path=str(tmp_path), config=None)
    m.excluded = {tmp_path}
    assert m._is_excluded(tmp_path / 'sub' / 'file.py') is True


def test_is_excluded_true_when_excluded_name_in_parts(tmp_path: Path) -> None:
    with patch('def_form.core.manager.find_pyproject_toml', return_value=None):
        m = _make_manager(path=str(tmp_path), config=None)
    other = tmp_path.parent / 'other_dir'
    other.mkdir(exist_ok=True)
    m.excluded = {other}
    p = Path('/any/other_dir/file.py')
    assert m._is_excluded(p) is True


def test_is_excluded_false_when_not_under_and_name_not_in_parts(tmp_path: Path) -> None:
    with patch('def_form.core.manager.find_pyproject_toml', return_value=None):
        m = _make_manager(path=str(tmp_path), config=None)
    m.excluded = {tmp_path / 'x'}
    assert m._is_excluded(tmp_path / 'file.py') is False


def test_iter_py_files_file_not_py_returns_nothing(tmp_path: Path) -> None:
    f = tmp_path / 'readme.txt'
    f.write_text('x')
    with patch('def_form.core.manager.find_pyproject_toml', return_value=None):
        m = _make_manager(path=str(f))
    m.excluded = set()
    assert list(m._iter_py_files()) == []


def test_iter_py_files_file_excluded_calls_ui_skipped(tmp_path: Path) -> None:
    py = tmp_path / 'f.py'
    py.write_text('x = 1')
    ui = MagicMock()
    with patch('def_form.core.manager.find_pyproject_toml', return_value=None):
        m = DefManager(path=str(py), ui=ui, config=None)
    m.excluded = {tmp_path}
    assert list(m._iter_py_files()) == []
    ui.skipped.assert_called_once()


def test_process_file_read_error_returns_empty(tmp_path: Path) -> None:
    f = tmp_path / 'x.py'
    f.write_text('def f(): pass')
    with patch('def_form.core.manager.find_pyproject_toml', return_value=None):
        m = _make_manager(path=str(tmp_path))
    with patch.object(Path, 'read_text', side_effect=OSError):
        tree, issues = m._process_file(f, m.checker_class)
    assert tree is None
    assert issues == []


def test_process_file_syntax_error_returns_empty(tmp_path: Path) -> None:
    import libcst as cst

    f = tmp_path / 'x.py'
    f.write_text('x = 1')
    with patch('def_form.core.manager.find_pyproject_toml', return_value=None):
        m = _make_manager(path=str(tmp_path))
    err = cst.ParserSyntaxError('syntax error', lines=(), raw_line=1, raw_column=0)
    with patch('def_form.core.manager.cst.parse_module', side_effect=err):
        tree, issues = m._process_file(f, m.checker_class)
    assert tree is None
    assert issues == []


def test_process_file_generic_exception_returns_empty(tmp_path: Path) -> None:
    f = tmp_path / 'x.py'
    f.write_text('def f(): pass')
    with patch('def_form.core.manager.find_pyproject_toml', return_value=None):
        m = _make_manager(path=str(tmp_path))

    def raise_in_visit(*args: object, **kwargs: object) -> None:
        raise RuntimeError('visit failed')

    with patch('def_form.core.manager.cst.metadata.MetadataWrapper') as MockWrapper:
        mock_wrapper = MagicMock()
        MockWrapper.return_value = mock_wrapper
        mock_wrapper.visit.side_effect = raise_in_visit
        tree, issues = m._process_file(f, m.checker_class)
    assert tree is None
    assert issues == []


def test_write_on_os_error_calls_ui_error(tmp_path: Path) -> None:
    ui = MagicMock()
    with patch('def_form.core.manager.find_pyproject_toml', return_value=None):
        m = DefManager(path=str(tmp_path), ui=ui, config=None)
    with patch.object(Path, 'write_text', side_effect=OSError('permission')):
        m._write(tmp_path / 'out.py', 'code')
    ui.console.error.assert_called_once()
    assert 'Exception occurred' in str(ui.console.error.call_args[0][0])
