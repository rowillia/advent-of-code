import os
from datetime import datetime
from typing import Any

from python.aoc_utils.finder import Day, get_days


def pytest_generate_tests(metafunc: Any) -> None:
    # Add the current year to years from datetime
    years = [datetime.now().year]
    if os.getenv("ADVENT_RUN_ALL_TESTS", "").lower() == "true":
        years = None
    days = get_days(years)
    metafunc.parametrize("day", [d for d in days], ids=[str(d) for d in days])


def test_day(day: Day) -> None:
    for part, answer in enumerate(day.example_answers):
        example_input = day.example_input
        if not isinstance(example_input, str):
            example_input = example_input[part]
        assert str(getattr(day.module, f"part{part + 1}")(example_input)) == answer
