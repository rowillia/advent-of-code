"""Helper functions for interactive Advent of Code development.

These functions provide easy access to puzzle inputs and example data
during interactive development with cell markers (# %%).
"""

from pathlib import Path
from typing import Any

from yaml import safe_load


def _get_project_root() -> Path:
    """Get the root directory of the Advent of Code project."""
    # This file is in aoc/utils/, so go up two levels
    return Path(__file__).parent.parent.parent


def solution_input(year: int, day: int) -> str:
    """Load the actual puzzle input for a given day.

    Args:
        year: The year of the puzzle (e.g., 2024)
        day: The day number (1-25)

    Returns:
        The puzzle input as a string, or empty string if file doesn't exist

    Example:
        >>> inp = solution_input(2024, 1)
    """
    input_file = _get_project_root() / "inputs" / str(year) / f"{day:02d}.txt"
    if input_file.exists():
        return input_file.read_text()
    return ""


def _load_example_yaml(year: int, day: int) -> dict[str, Any]:
    """Load and parse the example YAML file for a given day."""
    example_file = _get_project_root() / "examples" / str(year) / f"{day:02d}.yaml"
    if not example_file.exists():
        return {}
    return safe_load(example_file.read_text()) or {}


def example_input(year: int, day: int, part: int = 1) -> str:
    """Load the example input for a given day and part.

    Args:
        year: The year of the puzzle (e.g., 2024)
        day: The day number (1-25)
        part: The part number (1 or 2, default: 1)

    Returns:
        The example input as a string, or empty string if not found

    Example:
        >>> inp = example_input(2024, 1, part=1)
    """
    data = _load_example_yaml(year, day)
    if not data:
        return ""

    example_data = data.get("input", "")

    # Handle both single string and list of strings
    if isinstance(example_data, list):
        # List format: different inputs for each part
        idx = part - 1
        if 0 <= idx < len(example_data):
            return example_data[idx]
        return ""
    else:
        # Single string: same input for both parts
        return example_data


def example_answer(year: int, day: int, part: int) -> str:
    """Load the expected answer for a given day and part.

    Args:
        year: The year of the puzzle (e.g., 2024)
        day: The day number (1-25)
        part: The part number (1 or 2)

    Returns:
        The expected answer as a string, or empty string if not found

    Example:
        >>> answer = example_answer(2024, 1, part=1)
    """
    data = _load_example_yaml(year, day)
    if not data:
        return ""

    answers = data.get("answers", [])
    idx = part - 1
    if 0 <= idx < len(answers):
        return str(answers[idx])
    return ""
