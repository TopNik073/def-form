from typing import Optional, Union, Callable


def example_of_decorator(f: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper

def clear_def():
    return

def formatted_def(
        a,
        b: Optional[Union[int, str]] = None,
        c: int | str | None = None,
):
    return

def to_much_inline_args(
        to,
        much,
        inline,
        arguments,
):
    return

async def async_def():
    return

async def async_def_with_args(
        a,
        b,
        c,
):
    return

def to_much_inline_args_with_typehints(
        to: str,
        much,
        inline: int,
        arguments,
):
    return

def kw_args(
        def_,
        with_,
        *args,
        **kwargs,
):
    return

def def_kw_args_first(
        a,
        *args,
        b,
        **kwargs,
):
    return

@example_of_decorator
def def_with_decorator():
    return

@example_of_decorator
def def_with_decorator_and_args(
        a,
        b,
        c: Optional[str],
):
    return

def skipped_with_right_comment(a, b, c): # def-form: skip
    return

# def-form: skip
def skipped_with_up_comment(a, b, c):
    return

@example_of_decorator
def skipped_with_right_comment_and_decorator(a, b, c): # def-form: skip
    return

# def-form: skip
@example_of_decorator
def skipped_with_up_comment_and_decorator(
        a,
        b,
        c,
):
    return

def long_typehint_without_args(
        ) -> Optional[Union[int, str, list, dict[str, str], tuple[str], None, dict[str | int, list[str] | tuple[str, str, int, int] | None]]]:
    return

def long_typehint_with_args(
        a,
) -> Optional[Union[int, str, list, dict[str, str], tuple[str], None, dict[str | int, list[str] | tuple[str, str, int, int] | None]]]:
    return

def loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong_def_name(
        a,
):
    return


class ClassWithFunctions:
    def class_method(self):
        return

    def class_method_with_args(
            self,
            a,
            b,
    ):
        return

    def class_method_with_args_with_typehints(
            self,
            a: Optional[int],
            b: int,
            c,
    ):
        return

    async def async_def(self):
        return

    async def async_def_with_args(
            self,
            a,
            b,
            c,
    ):
        return

    @example_of_decorator
    async def async_def_with_args_and_decorator(
            self,
            a,
            b,
            c,
    ):
        return

    def skipped_with_right_comment(self, a, b, c): # def-form: skip
        return

    # def-form: skip
    def skipped_with_up_comment(self, a, b, c):
        return

    @example_of_decorator
    def def_with_decorator(self):
        return

    @example_of_decorator
    def def_with_decorator_and_args(
            self,
            a,
            b,
            c,
    ):
        return

    @staticmethod
    def static_method():
        return

    def def_with_kw_args(
            self,
            a,
            b,
            c,
            *args,
            **kwargs,
    ):
        return

    def def_with_kw_args_first(
            self,
            *args,
            a,
            b,
            c,
            **kwargs,
    ):
        return

    def class_method_with_long_typehint(
            self,
    ) -> Optional[Union[int, str, list, dict[str, str], tuple[str], None, dict[str | int, list[str] | tuple[str, str, int, int] | None]]]:
        return

    def class_method_with_long_typehint_with_args(
            self,
            a,
            b: int,
            c,
    )  -> Optional[Union[int, str, list, dict[str, str], tuple[str], None, dict[str | int, list[str] | tuple[str, str, int, int] | None]]]:
        return

    def class_method_with_loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong_name(
            self,
    ):
        return

    def class_method_with_loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong_name_and_arg(
            self,
            a,
    ):
        return
