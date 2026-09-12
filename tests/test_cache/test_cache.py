import json
from dataclasses import replace
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from unittest.mock import patch

import pytest

from def_form.core.cache import CACHE_DIR_NAME
from def_form.core.cache import DefCache
from def_form.core.cache import MANIFEST_NAME
from def_form.core.models import CacheManifest
from def_form.core.models import CacheSignature
from def_form.exceptions.cache import ToolVersionNotFoundException


SIGNATURE = CacheSignature(
    tool_version='1.2.3',
    max_def_length=100,
    max_inline_args=2,
    indent_size=4,
)


def _make_cache(
    root: Path,
    signature: CacheSignature | None = None,
    enabled: bool = True,
) -> DefCache:
    return DefCache(
        root=root,
        signature=signature if signature is not None else SIGNATURE,
        enabled=enabled,
    )


def _make_file(root: Path, name: str = 'a.py', content: str = 'x = 1\n') -> Path:
    path = root / name
    path.write_text(content, encoding='utf-8')
    return path


def test_compute_digest_is_stable_and_content_sensitive() -> None:
    assert DefCache.compute_digest('x = 1\n') == DefCache.compute_digest('x = 1\n')
    assert DefCache.compute_digest('x = 1\n') != DefCache.compute_digest('x = 2\n')


def test_tool_version_returns_installed_version() -> None:
    assert isinstance(DefCache.tool_version(), str)


def test_tool_version_raises_when_package_is_not_installed() -> None:
    with patch('def_form.core.cache.package_version', side_effect=PackageNotFoundError):
        with pytest.raises(ToolVersionNotFoundException):
            DefCache.tool_version()


def test_manifest_round_trips_through_dict() -> None:
    manifest = CacheManifest(manifest_version=1, signature='abc', files={'a.py': 'digest'})

    assert CacheManifest.from_dict(manifest.to_dict()) == manifest


@pytest.mark.parametrize(
    'data',
    [
        None,
        [1, 2, 3],
        {},
        {'manifest_version': '1', 'signature': 'abc', 'files': {}},
        {'manifest_version': 1, 'signature': 2, 'files': {}},
        {'manifest_version': 1, 'signature': 'abc', 'files': 'nope'},
    ],
)
def test_manifest_from_dict_rejects_malformed_data(data: object) -> None:
    assert CacheManifest.from_dict(data) is None


def test_manifest_from_dict_drops_entries_of_wrong_type() -> None:
    manifest = CacheManifest.from_dict(
        {'manifest_version': 1, 'signature': 'abc', 'files': {'a.py': 'digest', 'b.py': 42, 7: 'digest'}},
    )

    assert manifest is not None
    assert manifest.files == {'a.py': 'digest'}


def test_store_and_is_fresh(tmp_path: Path) -> None:
    cache = _make_cache(tmp_path)
    path = _make_file(tmp_path)
    digest = DefCache.compute_digest(path.read_text(encoding='utf-8'))

    assert cache.is_fresh(path, digest) is False

    cache.store(path, digest)

    assert cache.is_fresh(path, digest) is True
    assert cache.is_fresh(path, DefCache.compute_digest('other')) is False


def test_discard_drops_entry(tmp_path: Path) -> None:
    cache = _make_cache(tmp_path)
    path = _make_file(tmp_path)
    digest = DefCache.compute_digest(path.read_text(encoding='utf-8'))

    cache.store(path, digest)
    cache.discard(path)

    assert cache.is_fresh(path, digest) is False


def test_save_writes_manifest_and_gitignore(tmp_path: Path) -> None:
    cache = _make_cache(tmp_path)
    path = _make_file(tmp_path)
    digest = DefCache.compute_digest(path.read_text(encoding='utf-8'))

    cache.store(path, digest)
    cache.save()

    manifest_path = tmp_path / CACHE_DIR_NAME / MANIFEST_NAME
    assert manifest_path.is_file()
    assert (tmp_path / CACHE_DIR_NAME / '.gitignore').read_text(encoding='utf-8').endswith('*\n')

    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert data['manifest_version'] == 1
    assert data['files'] == {'a.py': digest}


def test_manifest_is_reused_across_instances(tmp_path: Path) -> None:
    path = _make_file(tmp_path)
    digest = DefCache.compute_digest(path.read_text(encoding='utf-8'))

    first = _make_cache(tmp_path)
    first.store(path, digest)
    first.save()

    second = _make_cache(tmp_path)
    assert second.is_fresh(path, digest) is True


def test_signature_change_invalidates_manifest(tmp_path: Path) -> None:
    path = _make_file(tmp_path)
    digest = DefCache.compute_digest(path.read_text(encoding='utf-8'))

    first = _make_cache(tmp_path)
    first.store(path, digest)
    first.save()

    second = _make_cache(tmp_path, signature=replace(SIGNATURE, max_inline_args=5))
    assert second.is_fresh(path, digest) is False


def test_broken_manifest_is_ignored(tmp_path: Path) -> None:
    cache_dir = tmp_path / CACHE_DIR_NAME
    cache_dir.mkdir()
    (cache_dir / MANIFEST_NAME).write_text('{not json', encoding='utf-8')

    path = _make_file(tmp_path)
    cache = _make_cache(tmp_path)

    assert cache.is_fresh(path, DefCache.compute_digest('x = 1\n')) is False


def test_manifest_with_unexpected_shape_is_ignored(tmp_path: Path) -> None:
    cache_dir = tmp_path / CACHE_DIR_NAME
    cache_dir.mkdir()
    (cache_dir / MANIFEST_NAME).write_text('[1, 2, 3]', encoding='utf-8')

    cache = _make_cache(tmp_path)

    assert cache.is_fresh(_make_file(tmp_path), DefCache.compute_digest('x = 1\n')) is False


def test_unknown_manifest_version_is_ignored(tmp_path: Path) -> None:
    path = _make_file(tmp_path)
    digest = DefCache.compute_digest(path.read_text(encoding='utf-8'))

    cache_dir = tmp_path / CACHE_DIR_NAME
    cache_dir.mkdir()
    (cache_dir / MANIFEST_NAME).write_text(
        json.dumps({'manifest_version': 999, 'signature': 'x', 'files': {'a.py': digest}}),
        encoding='utf-8',
    )

    assert _make_cache(tmp_path).is_fresh(path, digest) is False


def test_disabled_cache_never_hits_and_writes_nothing(tmp_path: Path) -> None:
    path = _make_file(tmp_path)
    digest = DefCache.compute_digest(path.read_text(encoding='utf-8'))

    cache = _make_cache(tmp_path, enabled=False)
    cache.store(path, digest)
    cache.save()

    assert cache.is_fresh(path, digest) is False
    assert not (tmp_path / CACHE_DIR_NAME).exists()


def test_save_prunes_entries_of_deleted_files(tmp_path: Path) -> None:
    path = _make_file(tmp_path)
    digest = DefCache.compute_digest(path.read_text(encoding='utf-8'))

    cache = _make_cache(tmp_path)
    cache.store(path, digest)
    cache.save()

    path.unlink()

    cache = _make_cache(tmp_path)
    cache.save()

    data = json.loads((tmp_path / CACHE_DIR_NAME / MANIFEST_NAME).read_text(encoding='utf-8'))
    assert data['files'] == {}


def test_paths_outside_root_are_stored_absolute(tmp_path: Path) -> None:
    root = tmp_path / 'project'
    root.mkdir()
    outside = _make_file(tmp_path, name='outside.py')

    cache = _make_cache(root)
    cache.store(outside, DefCache.compute_digest('x = 1\n'))
    cache.save()

    data = json.loads((root / CACHE_DIR_NAME / MANIFEST_NAME).read_text(encoding='utf-8'))
    assert list(data['files']) == [outside.resolve().as_posix()]


def test_clear_removes_directory(tmp_path: Path) -> None:
    cache = _make_cache(tmp_path)
    cache.store(_make_file(tmp_path), DefCache.compute_digest('x = 1\n'))
    cache.save()

    assert cache.clear() is True
    assert not (tmp_path / CACHE_DIR_NAME).exists()


def test_clear_returns_false_when_missing(tmp_path: Path) -> None:
    assert _make_cache(tmp_path).clear() is False


def test_clear_forgets_entries_in_memory(tmp_path: Path) -> None:
    cache = _make_cache(tmp_path)
    path = _make_file(tmp_path)
    digest = DefCache.compute_digest('x = 1\n')

    cache.store(path, digest)
    cache.save()
    cache.clear()

    assert cache.is_fresh(path, digest) is False


def test_cache_without_signature_is_disabled(tmp_path: Path) -> None:
    cache = DefCache(root=tmp_path, enabled=True)

    assert cache.enabled is False


def test_cache_without_signature_never_writes(tmp_path: Path) -> None:
    path = _make_file(tmp_path)
    digest = DefCache.compute_digest('x = 1\n')

    cache = DefCache(root=tmp_path, enabled=True)
    cache.store(path, digest)
    cache.save()

    assert cache.is_fresh(path, digest) is False
    assert not (tmp_path / CACHE_DIR_NAME).exists()


def test_cache_without_signature_ignores_an_existing_manifest(tmp_path: Path) -> None:
    path = _make_file(tmp_path)
    digest = DefCache.compute_digest('x = 1\n')

    stored = _make_cache(tmp_path)
    stored.store(path, digest)
    stored.save()

    assert DefCache(root=tmp_path, enabled=True).is_fresh(path, digest) is False


def test_cache_without_signature_can_still_be_cleared(tmp_path: Path) -> None:
    stored = _make_cache(tmp_path)
    stored.store(_make_file(tmp_path), DefCache.compute_digest('x = 1\n'))
    stored.save()

    assert DefCache(root=tmp_path, enabled=True).clear() is True
    assert not (tmp_path / CACHE_DIR_NAME).exists()
