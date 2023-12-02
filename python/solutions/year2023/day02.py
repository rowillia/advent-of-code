from collections import defaultdict
from dataclasses import dataclass
from functools import reduce
import re


LIMITS = {
    "red": 12,
    "green": 13,
    "blue": 14,
}


@dataclass
class GameTurn:
    cubes: list[tuple[int, str]]

    @classmethod
    def parse(cls, text: str) -> "GameTurn":
        pulls = [p.strip().split() for p in text.split(",")]
        return cls([(int(p[0]), p[1]) for p in pulls])

    def is_valid(self) -> bool:
        return all(c[0] <= LIMITS[c[1]] for c in self.cubes)


@dataclass
class CubeGame:
    num: int
    turns: list[GameTurn]

    def parse(text: str) -> "CubeGame":
        if match := re.match(r"Game (\d+): (.*)", text):
            return CubeGame(
                int(match.group(1)),
                [GameTurn.parse(t.strip()) for t in match.group(2).split(";")],
            )

    def is_valid(self) -> bool:
        return all(t.is_valid() for t in self.turns)

    def powerset(self) -> int:
        max_counts = defaultdict(int)
        for turn in self.turns:
            for cube in turn.cubes:
                max_counts[cube[1]] = max(max_counts[cube[1]], cube[0])
        return reduce(lambda x, y: x * y, max_counts.values())


@dataclass
class Day02:
    games: list[CubeGame]

    @classmethod
    def parse(cls, text: str) -> "Day02":
        return cls([CubeGame.parse(g.strip()) for g in text.splitlines()])


def part1(text: str) -> str | None:
    games = Day02.parse(text)
    return sum(g.num for g in games.games if g.is_valid())


def part2(text: str) -> str | None:
    games = Day02.parse(text)
    return sum(g.powerset() for g in games.games)
