import re
from typing import Tuple


LINE_RE = re.compile(r"(\d+)-(\d+),(\d+)-(\d+)")


def parse_line(line: str) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    if match := LINE_RE.match(line):
        a, b, c, d = [int(x) for x in match.groups()]
        return ((a, b), (c, d))
    raise Exception(f"Invalid Line: {line}")


def fully_overlap(x: Tuple[int, int], y: Tuple[int, int]) -> bool:
    return (x[0] <= y[0] and x[1] >= y[1]) or (y[0] <= x[0] and y[1] >= x[1])


def x_overlap_y(x: Tuple[int, int], y: Tuple[int, int]) -> bool:
    return (y[0] <= x[0] <= y[1]) or (y[0] <= x[1] <= y[1])


def partially_overlap(x: Tuple[int, int], y: Tuple[int, int]) -> bool:
    return x_overlap_y(x, y) or x_overlap_y(y, x)


def part1(text: str) -> int | None:
    return sum(int(fully_overlap(*parse_line(x))) for x in text.splitlines())


def part2(text: str) -> int | None:
    return sum(int(partially_overlap(*parse_line(x))) for x in text.splitlines())
