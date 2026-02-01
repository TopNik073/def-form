from typing import Callable, Optional


def example_of_decorator(f: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


@example_of_decorator
def def_with_decorator_and_args(a, b, c: Optional[str]):
    return
