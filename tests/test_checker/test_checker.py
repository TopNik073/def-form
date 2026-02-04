import pytest

from def_form.exceptions.base import BaseDefFormException
from def_form.exceptions.def_formatter import CheckCommandFoundAnIssue

from tests.helpers import normalize_issues
from tests.conftest import CASE_IDS


@pytest.mark.parametrize('case_id', CASE_IDS, indirect=True)
def test_check_case(
    case_id: str,
    case_manager,
    case_expected_issues: list[tuple[int, str]],
):
    if case_expected_issues:
        with pytest.raises(CheckCommandFoundAnIssue):
            case_manager.check()
    else:
        case_manager.check()

    got = normalize_issues(case_manager.issues)
    assert got == case_expected_issues
