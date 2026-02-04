from def_form.exceptions.base import BaseDefFormException
from def_form.exceptions.def_formatter import InvalidMultilineParamsIndentException
from def_form.core.rules.base import Rule
from def_form.core.rules.context import RuleContext


class RuleMultilineParamsIndent(Rule):
    def check(self, context: RuleContext) -> list[BaseDefFormException]:
        if context.is_single_line or context.has_correct_multiline_format:
            return []
        return [
            InvalidMultilineParamsIndentException(
                path=f'{context.filepath}:{context.line_no}',
                message=f'Invalid multiline function parameters indentation (expected {context.indent_size} spaces)',
            )
        ]
