from dataclasses import dataclass


@dataclass(frozen=True)
class RuleContext:
    filepath: str
    line_no: int
    line_length: int
    arg_count: int
    is_single_line: bool
    has_correct_multiline_format: bool
    indent_size: int
    max_def_length: int | None
    max_inline_args: int | None
