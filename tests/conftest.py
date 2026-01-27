from collections.abc import Callable

import pytest

from def_form.formatters.def_formatter import DefManager
from tests.constants import EXAMPLE_PATH
from tests.constants import EXPECTED_PATH
from tests.constants import FORMATTED_PATH
from tests.constants import MAX_DEF_LENGTH
from tests.constants import MAX_INLINE_ARGS


@pytest.fixture
def get_def_manager() -> DefManager:
    return DefManager(
        excluded=(),
        max_def_length=MAX_DEF_LENGTH,
        max_inline_args=MAX_INLINE_ARGS,
        path=EXAMPLE_PATH,
    )


@pytest.fixture
def get_correct_def_manager() -> DefManager:
    return DefManager(
        excluded=(),
        max_def_length=MAX_DEF_LENGTH,
        max_inline_args=MAX_INLINE_ARGS,
        path=EXPECTED_PATH,
    )


@pytest.fixture
def get_expected() -> str:
    with open(EXPECTED_PATH, encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def get_formatted() -> Callable[[], str]:
    def read() -> str:
        with open(FORMATTED_PATH, encoding='utf-8') as f:
            return f.read()

    return read
