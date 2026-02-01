import pytest

from def_form.core.rules.base import Rule
from def_form.core.rules.context import RuleContext


def test_rule_check_raises_not_implemented() -> None:
    class StubRule(Rule):
        def check(self, context: RuleContext):
            return super().check(context)

    rule = StubRule()
    ctx = RuleContext(
        filepath='x.py',
        line_no=1,
        line_length=50,
        arg_count=2,
        is_single_line=True,
        has_correct_multiline_format=True,
        indent_size=4,
        max_def_length=None,
        max_inline_args=None,
    )
    with pytest.raises(NotImplementedError):
        rule.check(ctx)
