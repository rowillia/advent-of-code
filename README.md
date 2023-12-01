# 🎄 Advent of Code 2022

## Usage

1. (Optional) Set the environment variable `ADVENT_SESSION_COOKIE` or add it to  to your adventofcode session cookie to automatically download your problem input.  This can be find in the "Application > Storage > Cookies" section of the Chrome Developer Tools while visiting https://adventofcode.com .

    <img width="509" alt="Screenshot 2023-11-28 at 5 35 34 PM" src="https://github.com/rowillia/advent2022/assets/808798/40d6f22e-9b55-405c-a56e-8b47b02ac7d2">

1. Generate the scaffolding for today's question
    ```bash
    poetry shell
    python -m python.run scaffold
    ```
1. Paste the sample input and answer(s) into `examples/{year}/{day}.yaml`.  For example:

    ```yaml
    input: |-
    A Y
    B X
    C Z
    answers:
    - 15
    - 12
    ```

Scaffolding will generate an empty solution file with 2 methods - `part1` and `part2`.

`python/solutions/{year}/dayXY.py`
```python
def part1(text: str) -> int | None:
    return None


def part2(text: str) -> int | None:
    return None
```

Unit Tests will be automatically generated based on the examples specified in the above yaml.  Simply run:

```bash
poetry run pytest
```

Once you are satisfied with today's answer, generate your answer with:

```bash
python -m python.run solve
```