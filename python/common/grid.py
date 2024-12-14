from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

from immutables import Map

from python.common.point import Point

T = TypeVar("T")


@dataclass(frozen=True)
class Grid(Generic[T]):
    entries: Map[Point, T]
    lower_right_bound: Point

    @classmethod
    def parse(cls, text: str, convert: Callable[[str], T]):
        result = {}
        row, col = None, None
        for row, line in enumerate(text.splitlines()):
            for col, value in enumerate(line):
                result[Point(col, row)] = convert(value)
        assert row is not None and col is not None
        return cls(Map(result), Point(col, row))
