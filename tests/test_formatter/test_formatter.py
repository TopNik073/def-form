import os
from collections.abc import Callable

from def_form.formatters.def_formatter import DefManager
from tests.constants import EXPECTED_TOTAL_ISSUES
from tests.constants import FORMATTED_PATH
from tests.mock_data import EXPECTED_ISSUES


def test_successful_format(get_def_manager: DefManager, get_expected: str, get_formatted: Callable[[], str]):
    get_def_manager.format(write_to=FORMATTED_PATH)
    assert len(get_def_manager.issues) == EXPECTED_TOTAL_ISSUES
    assert get_def_manager.issues == EXPECTED_ISSUES
    assert get_expected == get_formatted()

    os.remove(FORMATTED_PATH)


def test_no_need_format(get_correct_def_manager: DefManager):
    get_correct_def_manager.format()
    assert len(get_correct_def_manager.issues) == 0
