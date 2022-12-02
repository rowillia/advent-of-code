# 🎄 Advent of Code 2022

## Usage

1. (Optional) Set the environment variable `ADVENT_SESSION_COOKIE` to your adventofcode session cookie to automatically downlaod the input
1. Generate the scaffolding for today's question
    ```bash
    poetry shell
    python ./python/run.py scaffold
    ```
1. Paste the sample input into `examples/XY.txt` and sample answers into `examples/XY_answer.txt` (one line per part)

This will generate an empty solution file with 2 methods - `part1` and `part2`.

`python/solutions/dayXY.py`
```python
def part1(text: str) -> int | None:
    return ''


def part2(text: str) -> int | None:
    return ''
```

Unit Tests will be automatically generated based on the examples.  Simply run:

```bash
poetry run pytest
```