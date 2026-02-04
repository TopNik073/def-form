from typing import Optional, Union


def long_typehint_without_args() -> Optional[Union[int, str, list, dict[str, str], tuple[str], None, dict[str | int, list[str] | tuple[str, str, int, int] | None]]]:
    return
