from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def manhattan_distance(self, other: "Point") -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)
