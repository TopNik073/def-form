from pathlib import Path
from unittest.mock import patch

import pytest

from def_form.core import DefManager
from tests.helpers import normalize_issues
from tests.conftest import CASE_IDS


@pytest.mark.parametrize('case_id', CASE_IDS, indirect=True)
def test_format_case(
    case_id: str,
    case_dir: Path,
    case_manager: DefManager,
    case_expected_issues: list[tuple[int, str]],
    case_expected_content: str | None,
):
    def capture_write(dest, module: str):
        pass

    with patch.object(case_manager, '_write', side_effect=capture_write) as mocked_write:
        case_manager.format()

    got_issues = normalize_issues(case_manager.issues)
    assert got_issues == case_expected_issues, (
        f'case_id={case_id}: expected issues {case_expected_issues}, got {got_issues}'
    )

    if case_expected_content is not None:
        mocked_write.assert_called_once()
        assert mocked_write.call_args[1]['module'].strip() == case_expected_content.strip()
