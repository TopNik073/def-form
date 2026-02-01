from typing import Callable, Optional


def example_of_decorator(f: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


@example_of_decorator
def single_line_decorated_with_comment(a,  # decorated with comment
 b, c: Optional[str]):
    return
