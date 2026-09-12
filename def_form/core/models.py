from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from libcst import FunctionDef
from libcst import Module
from libcst._position import CodeRange

from def_form.exceptions.base import BaseDefFormException


@dataclass
class FunctionAnalysis:
    should_process: bool
    reason: str | None = None
    line_length: int | None = None
    arg_count: int | None = None
    line_no: int | None = None
    pos: CodeRange | None = None
    node: FunctionDef | None = None
    issues: list[BaseDefFormException] | None = None

    def __post_init__(self) -> None:
        if self.issues is None:
            self.issues = []


@dataclass(frozen=True)
class CacheSignature:
    """Everything a cached verdict depends on besides the file content itself

    Any change here means the stored verdicts were produced by different rules, so the
    whole manifest is dropped instead of being trusted
    """

    tool_version: str
    max_def_length: int | None
    max_inline_args: int | None
    indent_size: int | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CacheManifest:
    """On-disk form of the cache

    ``from_dict`` accepts only a well-formed manifest; whether its content may still be
    trusted is decided by the reader, which compares the version and the signature
    """

    manifest_version: int
    signature: str
    files: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Any) -> 'CacheManifest | None':
        if not isinstance(data, dict):
            return None

        manifest_version = data.get('manifest_version')
        signature = data.get('signature')
        files = data.get('files')

        if not isinstance(manifest_version, int) or not isinstance(signature, str) or not isinstance(files, dict):
            return None

        return cls(
            manifest_version=manifest_version,
            signature=signature,
            files={key: value for key, value in files.items() if isinstance(key, str) and isinstance(value, str)},
        )


@dataclass
class ProcessResult:
    """Outcome of running a processor over a single file

    ``ok`` is False when the file could not be read or parsed: such a file is never
    cached, because nothing was actually validated
    """

    ok: bool
    module: Module | None = None
    issues: list[BaseDefFormException] = field(default_factory=list)
