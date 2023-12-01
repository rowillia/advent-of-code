import bisect
from collections import defaultdict

from dataclasses import dataclass, field
import math
from typing import Dict, List, Tuple

from python.common.point import Point
from python.common.range_map import add_range


DIRECTIONS = [Point(0, 1), Point(-1, 1), Point(1, 1)]


@dataclass
class SandPit:
    occupied: Dict[int, List[Tuple[float, float]]] = field(
        default_factory=lambda: defaultdict(list)
    )
    bottom: int = 0

    def __contains__(self, item: Point) -> bool:
        row = self.occupied[item.y]
        if not row:
            return False
        idx = bisect.bisect(row, (item.x, math.inf))
        candidate_range = row[idx - 1]
        return candidate_range[0] <= item.x <= candidate_range[1]

    def drop_sand(self) -> bool:
        point = Point(500, 0)
        if point in self:
            return False
        while point.y < self.bottom:
            for candidate in (point + d for d in DIRECTIONS):
                if candidate not in self:
                    point = candidate
                    break
            else:
                self.merge_into(point.y, (point.x, point.x))
                return True
        return False

    def merge_into(self, row_num: int, col: Tuple[float, float]) -> None:
        row = self.occupied[row_num]
        if row_num > self.bottom:
            self.bottom = row_num
        add_range(row, col)

    @classmethod
    def parse(cls, text: str, add_floor: bool = False) -> "SandPit":
        result = SandPit()
        for line in text.splitlines():
            last: Point | None = None
            for coord in line.split(" -> "):
                x, y = [int(num) for num in coord.split(",")]
                point = Point(x, y)
                if last:
                    if last.y == point.y:
                        result.merge_into(
                            last.y, (min(point.x, last.x), max(point.x, last.x))
                        )
                    else:
                        for y in range(min(point.y, last.y), max(point.y, last.y) + 1):
                            result.merge_into(y, (last.x, last.x))
                last = point

        if add_floor:
            result.merge_into(result.bottom + 2, (-math.inf, math.inf))
        return result


def part1(text: str) -> int | None:
    s = SandPit.parse(text)
    ctr = 0
    while s.drop_sand():
        ctr += 1
    return ctr


def part2(text: str) -> int | None:
    s = SandPit.parse(text, True)
    ctr = 0
    while s.drop_sand():
        ctr += 1
    return ctr
