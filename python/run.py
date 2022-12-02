import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import click
import requests
from aoc_utils.finder import get_days


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--day", default=None, help="Day to run, defaults to latest", type=int)
def run(day: int | None) -> None:
    days = get_days()

    if day:
        current_day = next((x for x in days if x.day_number == day), None)
        if current_day is None:
            raise click.BadParameter(f"No solution yet for {day}")
    else:
        current_day = days[-1]

    print(f"🎄 Advent of Code: Day {current_day.day_number} 🎄")
    part1_answer = getattr(current_day.module, "part1")(current_day.solution_input)
    print(f"\t Part 1: {part1_answer}")
    part2_answer = getattr(current_day.module, "part2")(current_day.solution_input)
    if part1_answer is not None:
        print(f"\t Part 2: {part2_answer}")


@cli.command()
@click.option("--day", default=None, help="Day to run, defaults to latest", type=int)
def scaffold(day: int | None) -> None:
    day = day or datetime.now(ZoneInfo("America/New_York")).day
    session_cookie = os.getenv("ADVENT_SESSION_COOKIE", "")
    if session_cookie:
        day_input = requests.get(
            f"https://adventofcode.com/2022/day/{day}/input",
            cookies={"session": session_cookie},
        ).text
    else:
        day_input = ""
    project_dir = Path(__file__).resolve().parent
    input_file = project_dir / "inputs" / f"{day:02d}.txt"
    input_file.write_text(day_input)
    solution_file = project_dir / "solutions" / f"day{day:02d}.py"
    if not solution_file.exists():
        solution_file.write_text(
            """
def part1(text: str) -> int | None:
    return ''


def part2(text: str) -> int | None:
    return ''
    """
        )
    (project_dir / "examples" / f"{day:02d}.txt").touch()
    (project_dir / "examples" / f"{day:02d}_answer.txt").touch()


if __name__ == "__main__":
    cli()
