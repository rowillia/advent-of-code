from dataclasses import dataclass
from typing import List, Tuple

from python.common.graph import astar


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def manhattan_distance(self, other: "Point") -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)


DIRECTIONS = [
    Point(1, 0),
    Point(-1, 0),
    Point(0, 1),
    Point(0, -1),
]


@dataclass
class HeightMap:
    heights: List[List[int]]
    start: Point
    end: Point
    minimums: List[Point]

    def __getitem__(self, item: Point) -> int:
        return self.heights[item.y][item.x]

    def __contains__(self, item: Point) -> bool:
        return (0 <= item.x < len(self.heights[0])) and (
            0 <= item.y < len(self.heights)
        )

    @classmethod
    def parse(cls, text: str) -> "HeightMap":
        result: List[List[int]] = []
        start: Point | None = None
        end: Point | None = None
        minimums: List[Point] = []

        for row, line in enumerate(text.splitlines()):
            result.append([])
            for col, char in enumerate(line):
                if char == "S":
                    start = Point(col, row)
                    char = "a"
                elif char == "E":
                    end = Point(col, row)
                    char = "z"
                if char == "a":
                    minimums.append(Point(col, row))
                result[-1].append(-1 * (ord("a") - ord(char)))
        if not start or not end:
            raise Exception("Didn't find start or end")
        return HeightMap(result, start, end, minimums)

    def solve(self, all_minimums: bool = False) -> List[Point]:
        def neighbors(point: Point) -> List[Tuple[Point, int]]:
            result: List[Tuple[Point, int]] = []
            current_height = self[point]
            for direction in DIRECTIONS:
                candidate = point + direction
                if candidate in self and self[candidate] <= current_height + 1:
                    result.append((candidate, 1))
            return result

        def heuristic(p1: Point, p2: Point) -> int:
            return p1.manhattan_distance(p2)

        candidate = []
        if all_minimums:
            shortest = None
            for minimum in self.minimums:
                try:
                    candidate = astar(minimum, self.end, heuristic, neighbors)
                except Exception:
                    pass
                if shortest is None or len(candidate) < len(shortest):
                    shortest = candidate
            return shortest or []
        return astar(self.start, self.end, heuristic, neighbors)


def part1(text: str) -> int | None:
    height_map = HeightMap.parse(text)
    path = height_map.solve()
    return len(path) - 1


def part2(text: str) -> int | None:
    height_map = HeightMap.parse(text)
    path = height_map.solve(True)
    return len(path) - 1
