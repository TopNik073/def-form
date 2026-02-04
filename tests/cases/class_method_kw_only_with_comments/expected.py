class ClassWithFunctions:
    def class_method_kw_only_with_comments(
        self,
        *args,  # varargs in class
        b: str,  # keyword-only in class
        s: str,  # another keyword-only
        **kwargs,
    ):  # kwargs in class
        return
