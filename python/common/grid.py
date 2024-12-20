from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

from immutables import Map

from python.common.point import Point

T = TypeVar("T")


@dataclass(frozen=True)
class Grid(Generic[T]):
    entries: Map[Point, T]
    lower_right_bound: Point

    def render(self, value: T):
        return str(value)

    def __str__(self):
        result = []
        for row in range(self.lower_right_bound.y):
            current = []
            for col in range(self.lower_right_bound.x):
                current.append(self.render(self.entries[Point(col, row)]))
            result.append("".join(current))
        return "\n".join(result)

    @classmethod
    def parse(cls, text: str, convert: Callable[[str], T]):
        result = {}
        row, col = None, None
        for row, line in enumerate(text.splitlines()):
            for col, value in enumerate(line):
                result[Point(col, row)] = convert(value)
        assert row is not None and col is not None
        return cls(Map(result), Point(col + 1, row + 1))
