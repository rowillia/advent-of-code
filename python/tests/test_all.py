from typing import Any
from aoc_utils.finder import get_days, Day


def pytest_generate_tests(metafunc: Any) -> None:
    metafunc.parametrize("day", get_days())


def test_day(day: Day) -> None:
    for part, answer in enumerate(day.example_answers):
        assert str(getattr(day.module, f"part{part + 1}")(day.example_input)) == answer
