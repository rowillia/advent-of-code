import os
from datetime import datetime
from typing import Any

from aoc.utils.finder import Day, get_days


def pytest_generate_tests(metafunc: Any) -> None:
    # Add the current year to years from datetime
    current_year = datetime.now().year
    if datetime.now().month < 12:
        current_year -= 1
    years = [current_year]
    if os.getenv("ADVENT_RUN_ALL_TESTS", "").lower() == "true":
        years = None
    days = get_days(years)
    metafunc.parametrize("day", [d for d in days], ids=[str(d) for d in days])


def test_day(day: Day) -> None:
    for part, answer in enumerate(day.example_answers):
        example_input = day.example_input_for_part(part)
        assert str(getattr(day.module, f"part{part + 1}")(example_input)) == answer
