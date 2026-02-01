"""Rules layer: rule classes and runner.

The analyzer builds RuleContext and runs rules; it does not contain
any "what is a violation" logic — that lives in rule classes.
"""

from def_form.exceptions.base import BaseDefFormException

from def_form.core.rules.base import Rule
from def_form.core.rules.context import RuleContext
from def_form.core.rules.max_def_length import RuleMaxDefLength
from def_form.core.rules.max_inline_args import RuleMaxInlineArgs
from def_form.core.rules.multiline_params_indent import (
    RuleMultilineParamsIndent,
)

# Default rule set used when none is passed
DEFAULT_RULES: tuple[Rule, ...] = (
    RuleMaxDefLength(),
    RuleMaxInlineArgs(),
    RuleMultilineParamsIndent(),
)


def run_rules(
    context: RuleContext,
    rules: tuple[Rule, ...] | list[Rule] | None = None,
) -> list[BaseDefFormException]:
    """Run all rules on the context and return combined issues."""
    rule_list = rules if rules is not None else list(DEFAULT_RULES)
    issues: list[BaseDefFormException] = []
    for rule in rule_list:
        issues.extend(rule.check(context))
    return issues


__all__ = [
    'DEFAULT_RULES',
    'Rule',
    'RuleMaxDefLength',
    'RuleMaxInlineArgs',
    'RuleMultilineParamsIndent',
    'run_rules',
]
