from dataclasses import dataclass
from functools import cached_property
import itertools
import math
from typing import Dict, Iterable, List, Sequence, Tuple


@dataclass
class Point:
    x: int
    y: int

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)


DIRECTIONS = (Point(1, 0), Point(-1, 0), Point(0, 1), Point(0, -1))


@dataclass
class Map:
    heights: List[List[int]]

    def __getitem__(self, item: Point) -> int:
        return self.heights[item.y][item.x]

    def __setitem__(self, item: Point, value: int) -> None:
        self.heights[item.y][item.x] = value

    def __contains__(self, item: Point) -> bool:
        return (0 <= item.x < len(self.heights[0])) and (
            0 <= item.y < len(self.heights)
        )

    def enumerate_direction(
        self, start: Point, direction: Point
    ) -> Iterable[Tuple[Point, int]]:
        point = start
        while point in self:
            yield point, self[point]
            point += direction

    def enumerate(
        self, direction: Point | None = None
    ) -> Iterable[Iterable[Tuple[Point, int]]]:
        direction = direction or Point(1, 0)
        start = Point(0, 0)
        if direction.x < 0 or direction.y < 0:
            start = Point(
                direction.x % len(self.heights[0]), direction.y % len(self.heights)
            )
        point = start
        while point in self:
            yield self.enumerate_direction(point, direction)
            if direction.x == 0:
                point = Point(point.x + 1, start.y)
            else:
                point = Point(start.x, point.y + 1)

    def empty_clone(self) -> "Map":
        return Map([[0 for x in row] for row in self.heights])

    @classmethod
    def parse(cls, text: str) -> "Map":
        return cls([[int(x) for x in line] for line in text.splitlines()])

    def _tallest_in_direction(self, direction: Point) -> "Map":
        result = self.empty_clone()
        for order in self.enumerate(direction):
            tallest = -1
            for point, value in order:
                result[point] = tallest
                tallest = max(value, tallest)

        return result

    def _tallest_maps(self) -> Sequence["Map"]:
        return tuple([self._tallest_in_direction(x) for x in DIRECTIONS])

    def _compute_visible_map(self, height: int, direction: Point) -> "Map":
        result = self.empty_clone()
        for order in self.enumerate(direction):
            visible = 0
            for point, value in order:
                result[point] = visible
                if value >= height:
                    visible = 1
                else:
                    visible += 1
        return result

    @cached_property
    def _visible_maps(self) -> Dict[int, Sequence["Map"]]:
        return {
            x: tuple(
                [self._compute_visible_map(x, direction) for direction in DIRECTIONS]
            )
            for x in range(10)
        }

    def best_sceneic_score(self) -> int:
        visible_maps = self._visible_maps
        best = -1
        for point, value in itertools.chain.from_iterable(self.enumerate()):
            current_score = math.prod(x[point] for x in visible_maps[value])
            best = max(current_score, best)
        return best

    @property
    def visible_count(self) -> int:
        tallest_maps = self._tallest_maps()
        result = 0
        for point, value in itertools.chain.from_iterable(self.enumerate()):
            result += int(any(value > x[point] for x in tallest_maps))
        return result


def part1(text: str) -> int | None:
    return Map.parse(text).visible_count


def part2(text: str) -> int | None:
    return Map.parse(text).best_sceneic_score()
