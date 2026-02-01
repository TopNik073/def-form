import pytest

from def_form.cli.console import NullConsole
from def_form.cli.context import context
from def_form.cli.ui import NullUI
from def_form.core import DefManager

from tests.helpers import discover_cases
from tests.helpers import load_expected_content
from tests.helpers import load_expected_issues
from tests.helpers import MAX_DEF_LENGTH
from tests.helpers import MAX_INLINE_ARGS


_cases = discover_cases()
CASE_IDS = [name for name, _ in _cases]
CASE_DIR_BY_ID = {name: path for name, path in _cases}


def _manager_kwargs(path: str) -> dict:
    return {
        'config': '/nonexistent',
        'excluded': (),
        'max_def_length': MAX_DEF_LENGTH,
        'max_inline_args': MAX_INLINE_ARGS,
        'path': path,
        'ui': NullUI(console=NullConsole(context=context)),
    }


@pytest.fixture
def case_id(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture
def case_dir(case_id: str):
    return CASE_DIR_BY_ID[case_id]


@pytest.fixture
def case_source_path(case_dir) -> str:
    return str(case_dir / 'source.py')


@pytest.fixture
def case_expected_issues(case_dir):
    return load_expected_issues(case_dir)


@pytest.fixture
def case_expected_content(case_dir) -> str | None:
    return load_expected_content(case_dir)


@pytest.fixture
def case_manager(case_source_path: str) -> DefManager:
    return DefManager(**_manager_kwargs(case_source_path))
