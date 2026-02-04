from typing import Callable, Optional


def example_of_decorator(f: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


@example_of_decorator
def truly_single_line_decorated(
    a,
    b,
    c: Optional[str],
):  # decorated single line
    return
