from typing import Iterable, List


def split_on_value(stream: Iterable[str], break_value: str = "") -> Iterable[List[int]]:
    buffer: List[int] = []
    for value in stream:
        if value == break_value:
            yield buffer
            buffer = []
        else:
            buffer.append(int(value))
    yield buffer


def part1(text: str) -> str:
    return str(max([sum(x) for x in split_on_value(text.splitlines())]))


def part2(text: str) -> str:
    return str(
        sum(
            sorted([sum(x) for x in split_on_value(text.splitlines())], reverse=True)[
                :3
            ]
        )
    )
