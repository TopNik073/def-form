from pathlib import Path

MAX_DEF_LENGTH = 100
MAX_INLINE_ARGS = 2
EXPECTED_TOTAL_ISSUES = 62

src_path = Path(__file__).resolve().parent

EXAMPLE_PATH: str = str(src_path / 'mock_data/example.py')
EXPECTED_PATH: str = str(src_path / 'mock_data/expected.py')
FORMATTED_PATH: str = str(src_path / 'mock_data/formatted.py')
