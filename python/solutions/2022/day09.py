from dataclasses import astuple, dataclass, field
import math
from typing import List, Set


@dataclass(frozen=True)
class Point:
    x: int = 0
    y: int = 0

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, length: int) -> "Point":
        return Point(self.x * length, self.y * length)

    def dist(self, other: "Point") -> float:
        return math.dist(astuple(self), astuple(other))

    def move_towards(self, other: "Point") -> "Point":
        return Point(
            max(-1, min(1, other.x - self.x)),
            max(-1, min(1, other.y - self.y)),
        )


DIRECTIONS = {
    "R": Point(1, 0),
    "L": Point(-1, 0),
    "U": Point(0, 1),
    "D": Point(0, -1),
}


@dataclass
class RopeMap:
    knots: List[Point]

    tails_history: Set[Point] = field(default_factory=set)

    def move(self, direction: str, distance: int) -> None:
        self.tails_history.add(self.knots[-1])
        dir_vec = DIRECTIONS[direction]

        for _ in range(distance):
            self.knots[0] += dir_vec
            last_knot = self.knots[0]
            for idx in range(1, len(self.knots)):
                cur_dist = self.knots[idx].dist(last_knot)
                if cur_dist < 2:
                    break
                self.knots[idx] += self.knots[idx].move_towards(last_knot)
                last_knot = self.knots[idx]
                if idx == (len(self.knots) - 1):
                    self.tails_history.add(last_knot)


def part1(text: str) -> int | None:
    rope_map = RopeMap([Point() for _ in range(2)])
    for line in text.splitlines():
        direction, distance = line.split()
        rope_map.move(direction, int(distance))
    return len(rope_map.tails_history)


def part2(text: str) -> int | None:
    rope_map = RopeMap([Point() for _ in range(10)])
    for line in text.splitlines():
        direction, distance = line.split()
        rope_map.move(direction, int(distance))
    return len(rope_map.tails_history)
