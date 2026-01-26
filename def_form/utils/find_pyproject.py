from pathlib import Path


def find_pyproject_toml() -> Path | None:
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        candidate = parent / 'pyproject.toml'
        if candidate.is_file():
            return candidate
    return None
