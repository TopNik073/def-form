from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

from def_form.utils.find_pyproject import find_pyproject_toml


def test_find_pyproject_returns_path_when_in_cwd(tmp_path: Path) -> None:
    (tmp_path / 'pyproject.toml').write_text('[project]\nname = "x"')
    with patch.object(Path, 'cwd', return_value=tmp_path):
        result = find_pyproject_toml()
    assert result == str(tmp_path / 'pyproject.toml')


def test_find_pyproject_returns_none_when_no_file_in_any_parent() -> None:
    cwd = MagicMock(spec=Path)
    cwd.__truediv__ = lambda self, other: cwd._child if other == 'pyproject.toml' else MagicMock()
    cwd._child = MagicMock()
    cwd._child.is_file.return_value = False
    parent1 = MagicMock(spec=Path)
    parent1.__truediv__ = lambda self, other: parent1._child if other == 'pyproject.toml' else MagicMock()
    parent1._child = MagicMock()
    parent1._child.is_file.return_value = False
    cwd.parents = [parent1]
    with patch.object(Path, 'cwd', return_value=cwd):
        result = find_pyproject_toml()
    assert result is None


def test_find_pyproject_returns_path_when_in_parent() -> None:
    cwd = MagicMock(spec=Path)
    child_cwd = MagicMock()
    child_cwd.is_file.return_value = False
    cwd.__truediv__ = lambda self, other: child_cwd if other == 'pyproject.toml' else MagicMock()
    parent = MagicMock(spec=Path)
    parent_file = MagicMock()
    parent_file.is_file.return_value = True
    parent_file.__str__ = lambda self: '/fake/parent/pyproject.toml'
    parent.__truediv__ = lambda self, other: parent_file if other == 'pyproject.toml' else MagicMock()
    cwd.parents = [parent]
    with patch.object(Path, 'cwd', return_value=cwd):
        result = find_pyproject_toml()
    assert result == '/fake/parent/pyproject.toml'
