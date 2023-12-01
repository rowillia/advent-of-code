from typing import Any
from python.aoc_utils.finder import get_days, Day


def pytest_generate_tests(metafunc: Any) -> None:
    days = get_days()
    metafunc.parametrize("day", [d for d in days], ids=[str(d) for d in days])


def test_day(day: Day) -> None:
    for part, answer in enumerate(day.example_answers):
        assert str(getattr(day.module, f"part{part + 1}")(day.example_input)) == answer
