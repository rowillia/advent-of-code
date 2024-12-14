from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, order=True)
class Point:
    x: int
    y: int

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def __neg__(self) -> "Point":
        return Point(-self.x, -self.y)

    def manhattan_distance(self, other: "Point") -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def adjacent_points(
        self,
        diagonal: bool = True,
        allow_out_of_bounds: bool = False,
        upper_bound: "Point | None" = None,
    ) -> Iterable["Point"]:
        for x in range(self.x - 1, self.x + 2):
            for y in range(self.y - 1, self.y + 2):
                if not allow_out_of_bounds:
                    if x < 0 or y < 0:
                        continue
                    if upper_bound is not None and (
                        x > upper_bound.x or y > upper_bound.y
                    ):
                        continue
                if x == self.x and y == self.y:
                    continue
                if diagonal or (x == self.x or y == self.y):
                    yield Point(x, y)
