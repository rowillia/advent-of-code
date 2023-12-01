from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
import itertools
from typing import Dict, FrozenSet, List

from python.common.point import Point


class Direction(Enum):
    NORTH = Point(0, -1)
    NORTH_EAST = Point(1, -1)
    EAST = Point(1, 0)
    SOUTH_EAST = Point(1, 1)
    SOUTH = Point(0, 1)
    SOUTH_WEST = Point(-1, 1)
    WEST = Point(-1, 0)
    NORTH_WEST = Point(-1, -1)

    @cached_property
    def field(self) -> FrozenSet["Direction"]:
        directions = list(Direction)
        left = directions[(directions.index(self) - 1) % len(directions)]
        right = directions[(directions.index(self) + 1) % len(directions)]
        return frozenset((left, self, right))


@dataclass
class Field:
    elves: Dict[Point, int]
    direction_order: List[Direction] = field(
        default_factory=lambda: [
            Direction.NORTH,
            Direction.SOUTH,
            Direction.WEST,
            Direction.EAST,
        ]
    )

    def propose(self, point: Point) -> Point | None:
        if all((point + d.value) not in self.elves for d in Direction):
            return None
        for d in self.direction_order:
            if all((point + d1.value) not in self.elves for d1 in d.field):
                return point + d.value
        return None

    def round(self) -> bool:
        proposals = [(e, self.propose(e)) for e in self.elves]
        proposal_count = Counter((p[1] for p in proposals))
        moved = False
        for original, proposal in proposals:
            if proposal_count[proposal] == 1 and proposal is not None:
                del self.elves[original]
                self.elves[proposal] = 1
                moved = True
        first = self.direction_order.pop(0)
        self.direction_order.append(first)
        return moved

    @property
    def top_left(self) -> Point:
        return Point(min(p.x for p in self.elves), min(p.y for p in self.elves))

    @property
    def bottom_right(self) -> Point:
        return Point(max(p.x for p in self.elves), max(p.y for p in self.elves))

    @property
    def empty_spaces(self) -> int:
        bottom_right = self.bottom_right
        top_left = self.top_left
        all_spaces = ((bottom_right.x - top_left.x) + 1) * (
            (bottom_right.y - top_left.y) + 1
        )
        return all_spaces - len(self.elves)

    def __str__(self) -> str:
        result = []
        for y in range(self.top_left.y, self.bottom_right.y + 1):
            line = []
            for x in range(self.top_left.x, self.bottom_right.x + 1):
                if Point(x, y) in self.elves:
                    line.append("#")
                else:
                    line.append(".")
            result.append("".join(line))
        return "\n".join(result)

    @classmethod
    def parse(cls, text: str) -> "Field":
        elves = {}
        for y, line in enumerate(text.splitlines()):
            for x, char in enumerate(line):
                p = Point(x, y)
                if char == "#":
                    elves[p] = 1
        return Field(elves)


def part1(text: str) -> int | None:
    field = Field.parse(text)
    for _ in range(10):
        field.round()
    return field.empty_spaces


def part2(text: str) -> int | None:
    field = Field.parse(text)
    for round_count in itertools.count(start=1):
        if not field.round():
            break
    print(str(field))
    return round_count
