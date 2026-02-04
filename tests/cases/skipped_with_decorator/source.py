from typing import Callable


def example_of_decorator(f: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


@example_of_decorator
def skipped_with_up_comment_and_decorator(a, b, c):  # def-form: skip
    return
