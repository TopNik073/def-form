from def_form.exceptions.base import BaseDefFormException
from def_form.exceptions.def_formatter import DefStringTooLongException
from def_form.core.rules.base import Rule
from def_form.core.rules.context import RuleContext


class RuleMaxDefLength(Rule):
    def check(self, context: RuleContext) -> list[BaseDefFormException]:
        if not context.is_single_line:
            return []
        if not context.max_def_length or context.line_length <= context.max_def_length:
            return []
        return [
            DefStringTooLongException(
                path=f'{context.filepath}:{context.line_no}',
                message=f'Function definition too long ({context.line_length} > {context.max_def_length})',
            )
        ]
