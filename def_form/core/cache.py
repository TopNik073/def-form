import contextlib
import hashlib
import json
import os
import shutil
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path

from def_form.core.models import CacheManifest
from def_form.core.models import CacheSignature
from def_form.exceptions.cache import ToolVersionNotFoundException

PACKAGE_NAME = 'def-form'

CACHE_DIR_NAME = '.def_form_cache'
MANIFEST_NAME = 'manifest.json'
MANIFEST_VERSION = 1

GITIGNORE_NAME = '.gitignore'
GITIGNORE_CONTENT = '# Automatically created by def-form\n*\n'


class DefCache:
    """Maps every known-clean file to the sha256 of the source it was validated against.

    A file is stored only when it produced no issues, so a hit means "nothing to report,
    nothing to rewrite". Entries are trusted only while the signature stays the same.
    """

    def __init__(
        self,
        root: Path,
        signature: CacheSignature | None = None,
        enabled: bool = True,
    ) -> None:
        self.root: Path = root
        self.dir: Path = root / CACHE_DIR_NAME
        self.manifest_path: Path = self.dir / MANIFEST_NAME

        # A disabled cache neither reads nor writes the manifest, so it needs no signature
        self.signature: str = self.hash_signature(signature) if signature is not None else ''

        # And without a signature there is nothing to match a manifest against, so it stays off
        self.enabled: bool = enabled and bool(self.signature)

        self._entries: dict[str, str] = {}

        # True when _entries differs from what is on disk. Runs that hit the cache for
        # every file change nothing, and then save() must not rewrite the manifest
        self._dirty: bool = False

        if self.enabled:
            self._load()

    # --------------------------------------------------------------------- #
    # Hashing
    # --------------------------------------------------------------------- #

    @staticmethod
    def tool_version() -> str:
        try:
            return package_version(PACKAGE_NAME)
        except PackageNotFoundError as exc:
            raise ToolVersionNotFoundException(path=PACKAGE_NAME) from exc

    @staticmethod
    def compute_digest(code: str) -> str:
        return hashlib.sha256(code.encode('utf-8')).hexdigest()

    @staticmethod
    def hash_signature(signature: CacheSignature) -> str:
        payload = json.dumps(signature.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    # --------------------------------------------------------------------- #
    # Manifest I/O
    # --------------------------------------------------------------------- #

    def _load(self) -> None:
        try:
            raw = self.manifest_path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            return

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return

        manifest = CacheManifest.from_dict(data)
        if manifest is None or manifest.manifest_version != MANIFEST_VERSION or manifest.signature != self.signature:
            return

        self._entries = manifest.files

    def save(self) -> None:
        if not self.enabled:
            return

        self._prune()

        if not self._dirty:
            return

        if self._write_manifest(self._build_manifest()):
            self._dirty = False

    def _build_manifest(self) -> CacheManifest:
        return CacheManifest(
            manifest_version=MANIFEST_VERSION,
            signature=self.signature,
            files=dict(sorted(self._entries.items())),
        )

    def _write_manifest(self, manifest: CacheManifest) -> bool:
        tmp_path = self.dir / f'{MANIFEST_NAME}.{os.getpid()}.tmp'

        try:
            self.dir.mkdir(parents=True, exist_ok=True)
            self._write_gitignore()

            tmp_path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding='utf-8')
            tmp_path.replace(self.manifest_path)
        except OSError:
            with contextlib.suppress(OSError):
                tmp_path.unlink(missing_ok=True)

            return False

        return True

    def _write_gitignore(self) -> None:
        gitignore = self.dir / GITIGNORE_NAME

        if gitignore.exists():
            return

        gitignore.write_text(GITIGNORE_CONTENT, encoding='utf-8')

    def clear(self) -> bool:
        if not self.dir.is_dir():
            return False

        shutil.rmtree(self.dir, ignore_errors=True)

        self._entries = {}
        self._dirty = False

        return not self.dir.exists()

    # --------------------------------------------------------------------- #
    # Entries
    # --------------------------------------------------------------------- #

    def _key(self, path: Path) -> str:
        resolved = Path(path).resolve()

        try:
            return resolved.relative_to(self.root).as_posix()
        except ValueError:
            return resolved.as_posix()

    def _resolve(self, key: str) -> Path:
        path = Path(key)
        return path if path.is_absolute() else self.root / path

    def _prune(self) -> None:
        stale = [key for key in self._entries if not self._resolve(key).is_file()]

        for key in stale:
            del self._entries[key]
            self._dirty = True

    def is_fresh(
        self,
        path: Path,
        digest: str,
    ) -> bool:
        if not self.enabled:
            return False

        return self._entries.get(self._key(path)) == digest

    def store(
        self,
        path: Path,
        digest: str,
    ) -> None:
        if not self.enabled:
            return

        key = self._key(path)

        if self._entries.get(key) == digest:
            return

        self._entries[key] = digest
        self._dirty = True

    def discard(self, path: Path) -> None:
        if not self.enabled:
            return

        if self._entries.pop(self._key(path), None) is not None:
            self._dirty = True
