from pathlib import Path
from unittest.mock import patch

from def_form.utils.find_cache_root import find_cache_root


def test_returns_the_current_directory(tmp_path: Path) -> None:
    with patch.object(Path, 'cwd', return_value=tmp_path):
        assert find_cache_root() == tmp_path


def test_follows_the_current_directory(tmp_path: Path) -> None:
    nested = tmp_path / 'src' / 'package'
    nested.mkdir(parents=True)

    with patch.object(Path, 'cwd', return_value=nested):
        assert find_cache_root() == nested


def test_returns_an_absolute_path() -> None:
    assert find_cache_root().is_absolute()
