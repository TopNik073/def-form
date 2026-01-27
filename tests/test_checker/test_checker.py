import pytest

from def_form.exceptions.base import BaseDefFormException
from def_form.formatters.def_formatter import DefManager
from tests.constants import EXPECTED_TOTAL_ISSUES
from tests.mock_data import EXPECTED_ISSUES


def test_failed_check(get_def_manager: DefManager):
    with pytest.raises(BaseDefFormException):
        get_def_manager.check()

    assert get_def_manager.issues == EXPECTED_ISSUES
    assert len(get_def_manager.issues) == EXPECTED_TOTAL_ISSUES


def test_successful_check(get_correct_def_manager: DefManager):
    get_correct_def_manager.check()
    assert len(get_correct_def_manager.issues) == 0
