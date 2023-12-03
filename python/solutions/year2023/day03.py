from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Self

from python.common.point import Point


@dataclass
class Schematic:
    symbols: dict[Point, str]
    numbers: dict[Point, str]

    def adjacent_symbols(self, point: Point, number: str) -> set[Point]:
        one_right = Point(1, 0)
        result = set()
        for _ in range(len(number)):
            for adj_point in point.adjacent_points():
                if adj_point in self.symbols:
                    result.add(adj_point)
            point += one_right
        return result

    def symbol_adjacent_points(self) -> Iterable[int]:
        for point, number in self.numbers.items():
            if self.adjacent_symbols(point, number):
                yield int(number)

    def gears(self) -> Iterable[int]:
        gears = defaultdict(set)
        for number_point, number in self.numbers.items():
            adjacent_symbols = self.adjacent_symbols(number_point, number)
            for symbol_point in adjacent_symbols:
                if self.symbols[symbol_point] == "*":
                    gears[symbol_point].add(number_point)
        for gear in gears.values():
            if len(gear) == 2:
                left, right = gear
                yield int(self.numbers[left]) * int(self.numbers[right])

    @classmethod
    def parse(cls, text: str) -> Self:
        symbols = {}
        numbers = {}
        for y, line in enumerate(text.splitlines()):
            current_number = ""
            for x, char in reversed(list(enumerate(line))):
                if char == ".":
                    if current_number:
                        numbers[Point(x + 1, y)] = current_number
                    current_number = ""
                    continue
                point = Point(x, y)
                if char.isdigit():
                    current_number = char + current_number
                else:
                    symbols[point] = char
                    if current_number:
                        numbers[Point(x + 1, y)] = current_number
                    current_number = ""

            if current_number:
                numbers[Point(0, y)] = current_number
        return cls(symbols, numbers)


def part1(text: str) -> int | None:
    schematic = Schematic.parse(text)
    symbol_adjacent_points = list(Schematic.parse(text).symbol_adjacent_points())
    return sum(symbol_adjacent_points)


def part2(text: str) -> int | None:
    schematic = Schematic.parse(text)
    gears = list(Schematic.parse(text).gears())
    return sum(gears)
