import math
from functools import reduce


def roots(r: int, m: int) -> tuple[int, int]:
    discriminant = r**2 - 4 * (m + 1)
    root1 = (-r + math.sqrt(discriminant)) / (-2)
    root2 = (-r - math.sqrt(discriminant)) / (-2)
    return math.ceil(root1), math.floor(root2)


def parse_line(text: str) -> list[int]:
    return [int(x) for x in text.split(":")[1].split()]


def part1(text: str) -> int | None:
    time_str, distance_str = text.splitlines()
    races = zip(parse_line(time_str), parse_line(distance_str))
    winners = [roots(time, distance) for time, distance in races]
    scores = [(right - left + 1) for left, right in winners]
    return reduce(lambda x, y: x * y, scores)


def part2(text: str) -> int | None:
    time_str, distance_str = text.splitlines()
    time = int("".join(time_str.split(":")[1].split()))
    distance = int("".join(distance_str.split(":")[1].split()))
    l1, r = roots(time, distance)
    return r - l1 + 1
