import json
from pathlib import Path

from def_form.exceptions.base import BaseDefFormException


MAX_DEF_LENGTH = 100
MAX_INLINE_ARGS = 2


def get_case_dir() -> Path:
    return Path(__file__).resolve().parent / 'cases'


def discover_cases() -> list[tuple[str, Path]]:
    cases_dir = get_case_dir()
    if not cases_dir.is_dir():
        return []
    result: list[tuple[str, Path]] = []
    for path in sorted(cases_dir.iterdir()):
        if path.is_dir() and (path / 'source.py').is_file():
            result.append((path.name, path))
    return result


def normalize_issues(issues: list[BaseDefFormException]) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for exc in issues:
        path_str = getattr(exc, 'path', '')
        if ':' in path_str:
            line_str = path_str.rsplit(':', 1)[-1]
            try:
                line_no = int(line_str)
            except ValueError:
                line_no = 0
        else:
            line_no = 0
        out.append((line_no, type(exc).__name__))
    return sorted(out)


def load_expected_issues(case_dir: Path) -> list[tuple[int, str]]:
    path = case_dir / 'expected_issues.json'
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding='utf-8'))
    return [(_item['line'], _item['type']) for _item in data]


def load_expected_content(case_dir: Path) -> str | None:
    path = case_dir / 'expected.py'
    if not path.is_file():
        return None
    return path.read_text(encoding='utf-8')
