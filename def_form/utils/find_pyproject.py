from pathlib import Path


def find_pyproject_toml() -> str | None:
    current = Path.cwd()
    for parent in [current, *list(current.parents)]:
        candidate = parent / 'pyproject.toml'
        if candidate.is_file():
            return str(candidate)
    return None
