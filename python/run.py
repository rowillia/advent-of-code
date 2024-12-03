import os
import textwrap
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import click
import requests
import yaml
from anthropic import Anthropic
from bs4 import BeautifulSoup, Tag

from python.aoc_utils.finder import get_days


@click.group()
def cli() -> None:
    pass


PARSE_QUESTION_PROMPT = """
You are helping a user solve problems for the "Advent of Code" challenge.
You are helping them parse out the test cases from the problem definition above.
The problem may have 1 or 2 parts.

You should produce a yaml file with 2 fields: input and answers.
input should contain the problem input, and answers should contain the expected answer for each part.
input should always be a string, but answer can be any type as long as it can be coerced to a string with type casting.
Some problems have the same input for both parts.  If the question only has 1 part, only generate 1 input and 1 answer.

Same input, multiple part answer example:
```
input: |-
  Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
  Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
  Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
  Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
  Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green
answers:
- 8
- 2286
```


Different input, different answer example:
```
input:
  - |-
    1abc2
    pqr3stu8vwx
    a1b2c3d4e5f
    treb7uchet
  - |-
    two1nine
    eightwothree
    abcone2threexyz
    xtwone3four
    4nineeightseven2
    zoneight234
    7pqrstsixteen
answers:
  - 142
  - 281
```

What is the YAML for the provided question above enclosed within the `<advent_of_code_problem>` xml tag?

Only respond with the proprerly formatted yaml in a code block and nothing else.
"""


def parse_article(soup: Tag, width: int = 80) -> str:
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Add newlines around headings
    for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p"]):
        heading.insert_after("\n")

    # Convert lists to markdown format
    for list_tag in soup.find_all(["ul", "ol"]):
        is_ordered = list_tag.name == "ol"
        for i, item in enumerate(list_tag.find_all("li", recursive=False), 1):
            # Determine list marker
            if is_ordered:
                marker = f"  {i}. "
            else:
                marker = "  * "

            # Add marker to beginning of list item
            if item.string:
                item.string.replace_with(marker + item.string)
            else:
                item.insert(0, marker)

    # Get text and wrap each line
    text = soup.get_text()
    wrapped_lines = [textwrap.fill(line, width=width) for line in text.splitlines()]

    return "\n".join(wrapped_lines)


def convert_to_plain_text(response_text: str, width: int = 80) -> str:
    # Parse HTML
    soup = BeautifulSoup(response_text, "html.parser")

    articles = soup.find_all("article")
    result = ""
    for soup in articles:
        if not isinstance(soup, Tag):
            raise Exception("Could not find article tag in HTML")
        result += parse_article(soup, width=width) + "\n"
    return result.strip()


def get_test_yaml_from_problem(problem_text: str) -> str:
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
    default_answer = textwrap.dedent("""\
        input: |-

        answers:
        -
    """)
    if not anthropic_api_key:
        return default_answer
    yaml_lead_in = "input: |-"
    anthropic_client = Anthropic(api_key=anthropic_api_key)
    response = anthropic_client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"<advent_of_code_problem>\n{problem_text}\n<advent_of_code_problem>",
            },
            {
                "role": "user",
                "content": PARSE_QUESTION_PROMPT,
            },
            {"role": "assistant", "content": f"```yaml\n{yaml_lead_in}"},
        ],
        model="claude-3-5-sonnet-20241022",
    )
    result_text = response.content[0].text  # type: ignore
    result_text = result_text.replace("```", "")
    try:
        claude_yaml = yaml_lead_in + result_text
        yaml.safe_load(claude_yaml)
        return claude_yaml
    except yaml.YAMLError:
        print("Warning: AI was unable to parse the question for the sample data")
        return default_answer


@cli.command()
@click.option("--day", default=None, help="Day to run, defaults to latest", type=int)
@click.option("--year", default=None, help="Year to run, defaults to latest", type=int)
def solve(day: int | None, year: int | None = None) -> None:
    now = datetime.now(ZoneInfo("America/New_York"))
    year = year or now.year
    days = get_days([year])

    if day:
        current_day = next((x for x in days if x.day_number == day), None)
        if current_day is None:
            raise click.BadParameter(f"No solution yet for {day}")
    else:
        current_day = days[-1]

    print(f"🎄 Advent of Code {year}: Day {current_day.day_number} 🎄")
    part1_answer = current_day.module.part1(current_day.solution_input)
    print(f"Part 1:\n{part1_answer}\n\n")
    if part1_answer is not None:
        part2_answer = current_day.module.part2(current_day.solution_input)
        print(f"Part 2:\n{part2_answer}")


@cli.command()
@click.option("--day", default=None, help="Day to run, defaults to latest", type=int)
@click.option("--year", default=None, help="Year to run, defaults to latest", type=int)
def scaffold(day: int | None, year: int | None) -> None:
    now = datetime.now(ZoneInfo("America/New_York"))
    day = min(25, day or now.day)
    year = year or now.year
    session_cookie = os.getenv("ADVENT_SESSION_COOKIE", "")
    session_file = Path.home() / ".adventofcode.session"
    if not session_cookie and session_file.exists():
        session_cookie = session_file.read_text()

    if session_cookie:
        cookies = {"session": session_cookie}
        day_input = requests.get(
            f"https://adventofcode.com/{year}/day/{day}/input",
            cookies=cookies,
        ).text
    else:
        day_input = ""
        cookies = None

    problem_text = convert_to_plain_text(
        requests.get(f"https://adventofcode.com/{year}/day/{day}", cookies=cookies).text
    )

    project_dir = Path(__file__).resolve().parent
    inputs_dir = project_dir.parent / "inputs" / str(year)
    examples_dir = project_dir.parent / "examples" / str(year)
    solutions_dir = project_dir / "solutions" / f"year{year}"
    for directory in [inputs_dir, examples_dir, solutions_dir]:
        if not directory.exists():
            directory.mkdir(parents=True)
    input_file = inputs_dir / f"{day:02d}.txt"
    input_file.write_text(day_input)
    solution_file = solutions_dir / f"day{day:02d}.py"
    if not solution_file.exists():
        solution_file.write_text(
            textwrap.dedent("""\
                \"\"\"
                \"\"\"

                def part1(text: str) -> str | None:
                    return None


                def part2(text: str) -> str | None:
                    return None
                """)
        )

    with solution_file.open("r+") as f:
        content = f.read()
        start_index = content.find('"""')
        end_index = content.find('"""', start_index + 3) + 3
        if start_index != -1 and end_index != -1:
            content = content[:start_index] + content[end_index:]
        f.seek(0, 0)
        f.write(f'"""\n{problem_text}"""' + content)

    (examples_dir / f"{day:02d}.yaml").write_text(
        get_test_yaml_from_problem(problem_text)
    )


if __name__ == "__main__":
    cli()
