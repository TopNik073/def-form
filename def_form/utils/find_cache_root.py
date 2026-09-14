from pathlib import Path


def find_cache_root() -> Path:
    return Path.cwd()
