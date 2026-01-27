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

def wrong_formatted_def(
    a,
    b: Optional[Union[int, str]] = None,
):
    return

def with_comments(
    a,  # this is an argument
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

def single_line_with_comment_first(
    a,  # first param comment
    b,
    c,
):
    return

def single_line_with_comment_middle(
    a,
    b,  # middle param comment
    c,
):
    return

def single_line_with_comment_last(
    a,
    b,
    c,
):  # end comment
    return

def single_line_with_multiple_comments(
    a,  # first comment
    b,  # second comment
    c,
):  # third comment
    return

def single_line_with_comment_and_default(
    a,  # param with default
    b: int = 42,
    c: str = "test",
):
    return

def single_line_with_comment_and_typehint(
    a: int,  # typed param
    b: str,
    c: Optional[int] = None,
):
    return

def single_line_with_comment_and_args(
    a,  # regular param
    *args,  # varargs comment
    **kwargs,
):  # keyword args comment
    return

def truly_single_line_with_comment(
    a,
    b,
    c,
):  # truly single line
    return

def truly_single_line_with_comment_first(
    a,
    b,
    c,
):  # comment at end of signature
    return

def truly_single_line_with_type_and_comment(
    a: int,
    b: str,
    c: Optional[int] = None,
):  # all in one line
    return

def truly_single_line_with_args_comment(
    a,
    *args,
    **kwargs,
):  # args and kwargs
    return

async def async_def():
    return

async def async_def_with_args(
    a,
    b,
    c,
):
    return

async def async_single_line_with_comment(
    a,  # async with comment
    b,
    c,
):
    return

async def truly_async_single_line_with_comment(
    a,
    b,
    c,
):  # async single line
    return

def to_much_inline_args_with_typehints(
    to: str,
    much,
    inline: int,
    arguments,
):
    return

def single_line_with_comment_and_complex_type(
    a: Optional[Union[int, str]],  # complex type
    b: dict[str, int] = {},
    c: list[str] = [],
):
    return

def truly_single_line_with_complex_type(
    a: Optional[Union[int, str]],
    b: dict[str, int] = {},
    c: list[str] = [],
):  # complex types in one line
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

def single_line_kw_only_with_comments(
    a,
    *args,  # varargs
    b: str,  # keyword-only
    c: int = 10,  # keyword-only with default
    **kwargs,
):  # kwargs
    return

def truly_single_line_kw_only(
    a,
    *args,
    b: str,
    c: int = 10,
    **kwargs,
):  # kw-only in one line
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

@example_of_decorator
def single_line_decorated_with_comment(
    a,  # decorated with comment
    b,
    c: Optional[str],
):
    return

@example_of_decorator
def truly_single_line_decorated(
    a,
    b,
    c: Optional[str],
):  # decorated single line
    return

def skipped_with_right_comment(a, b, c): # def-form: skip
    return

# def-form: skip
def skipped_with_up_comment(a, b, c):
    return

@example_of_decorator
def skipped_with_right_comment_and_decorator(a, b, c): # def-form: skip
    return

@example_of_decorator
def skipped_with_up_comment_and_decorator(a, b, c):  # def-form: skip
    return

def long_typehint_without_args() -> Optional[Union[int, str, list, dict[str, str], tuple[str], None, dict[str | int, list[str] | tuple[str, str, int, int] | None]]]:
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

    def class_method_single_line_with_comment(
        self,
        a,  # class method comment
        b,
        c,
    ):
        return

    def truly_class_method_single_line(
        self,
        a,
        b,
        c,
    ):  # class method single line
        return

    def class_method_with_args_with_typehints(
        self,
        a: Optional[int],
        b: int,
        c,
    ):
        return

    def class_method_single_line_with_typehint_comment(
        self,
        a: int,  # typed comment
        b: str,
        c: Optional[int] = None,
    ):
        return

    def truly_class_method_with_types(
        self,
        a: int,
        b: str,
        c: Optional[int] = None,
    ):  # class method with types
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

    async def async_class_method_single_line(
        self,
        a,  # async class method
        b,
        c,
    ):
        return

    async def truly_async_class_method(
        self,
        a,
        b,
        c,
    ):  # async class method single line
        return

    @example_of_decorator
    async def async_def_with_args_and_decorator(
        self,
        a,
        b,
        c,
    ):
        return

    @example_of_decorator
    async def async_class_method_with_comment(
        self,
        a,  # decorated async
        b,
        c,
    ):
        return

    @example_of_decorator
    async def truly_async_decorated_class_method(
        self,
        a,
        b,
        c,
    ):  # decorated async class method
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

    def def_with_kw_only_args(
        self,
        *args,
        b: str,
        s: str,
        **kwargs,
    ):
        return

    def class_method_kw_only_with_comments(
        self,
        *args,  # varargs in class
        b: str,  # keyword-only in class
        s: str,  # another keyword-only
        **kwargs,
    ):  # kwargs in class
        return

    def truly_class_method_kw_only(
        self,
        *args,
        b: str,
        s: str,
        **kwargs,
    ):  # kw-only in class single line
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

    def class_method_single_line_with_defaults(
        self,
        a: int = 1,  # default value
        b: str = "test",  # another default
        c: Optional[int] = None,
    ):  # optional default
        return

    def truly_class_method_with_defaults(
        self,
        a: int = 1,
        b: str = "test",
        c: Optional[int] = None,
    ):  # defaults in class
        return

def single_line_with_return_type_comment(a: int, b: str) -> bool:  # return type comment
    return True

def truly_single_line_with_return_type(a: int, b: str) -> bool:  # return type in one line
    return True

def single_line_with_all_features(
    a: int,  # typed with comment
    b: str = "default",  # default with comment
    *args,  # varargs with comment
    c: int = 10,  # keyword-only with comment
    **kwargs,
) -> bool:  # kwargs and return type
    return True

def truly_single_line_all_features(
    a: int,
    b: str = "default",
    *args,
    c: int = 10,
    **kwargs,
) -> bool:  # all features in one line
    return True
