from def_form.exceptions.base import BaseDefFormException
from def_form.exceptions.def_formatter import TooManyInlineArgumentsException
from def_form.core.rules.base import Rule
from def_form.core.rules.context import RuleContext


class RuleMaxInlineArgs(Rule):
    def check(self, context: RuleContext) -> list[BaseDefFormException]:
        if not context.is_single_line:
            return []
        if not context.max_inline_args or context.arg_count <= context.max_inline_args:
            return []
        return [
            TooManyInlineArgumentsException(
                path=f'{context.filepath}:{context.line_no}',
                message=f'Too many inline args ({context.arg_count} > {context.max_inline_args})',
            )
        ]
