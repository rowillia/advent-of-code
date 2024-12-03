from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Set, Tuple

from python.common.point import Point


@dataclass(frozen=True)
class Shape:
    cells: FrozenSet[Point]
    height: int

    @classmethod
    def parse(cls, text: str) -> "Shape":
        cells: Set[Point] = set()
        row = 0
        for row, line in enumerate(reversed(text.splitlines())):
            for col, char in enumerate(line.strip()):
                if char == "#":
                    cells.add(Point(col, row))
        return Shape(frozenset(cells), row + 1)

    def offset(self, offset: Point) -> "Shape":
        return Shape(frozenset(cell + offset for cell in self.cells), self.height)

    def intersects(self, offset: Point, other: Set[Point]) -> bool:
        return bool(other.intersection(self.offset(offset).cells))


SHAPES = [
    Shape.parse("####"),
    Shape.parse(
        """.#.
           ###
           .#."""
    ),
    Shape.parse(
        """..#
           ..#
           ###"""
    ),
    Shape.parse(
        """#
           #
           #
           #"""
    ),
    Shape.parse(
        """##
           ##"""
    ),
]


DOWN = Point(0, -1)
MOVES = {True: Point(-1, 0), False: Point(1, 0)}

FLOOR = {Point(x, 0) for x in range(7)}


@dataclass
class TetrisBoard:
    moves: List[bool]
    occupied: Set[Point] = field(default_factory=lambda: FLOOR.copy())
    current_move: int = 0
    current_shape: int = 0
    tallest_point: int = 0

    @classmethod
    def parse(cls, text: str) -> "TetrisBoard":
        return TetrisBoard([x == "<" for x in text])

    def draw(self, shape: Shape | None = None) -> List[str]:
        output = ["+-------+"]
        for y in range(1, self.tallest_point + 10):
            row = "|"
            for x in range(7):
                p = Point(x, y)
                if p in self.occupied:
                    row += "#"
                else:
                    if shape and p in shape.cells:
                        row += "@"
                    else:
                        row += "."
            row += "|"
            output.append(row)
        return list(reversed(output))

    def play_round(self) -> Tuple[int, int, int]:
        shape = SHAPES[self.current_shape]
        offset = Point(2, self.tallest_point + 4)
        while True:
            next_move = offset + MOVES[self.moves[self.current_move]]
            next_shape = shape.offset(next_move)
            left = min(p.x for p in next_shape.cells)
            right = max(p.x for p in next_shape.cells)
            if (
                not shape.intersects(next_move, self.occupied)
                and left >= 0
                and right < 7
            ):
                offset = next_move
            self.current_move = (self.current_move + 1) % len(self.moves)
            next_move = offset + DOWN
            next_shape = shape.offset(next_move)
            if shape.intersects(next_move, self.occupied):
                break
            else:
                offset = next_move
        shape = shape.offset(offset)
        self.occupied = self.occupied.union(shape.cells)
        self.tallest_point = max(max(p.y for p in shape.cells), self.tallest_point)
        self.current_shape = (self.current_shape + 1) % len(SHAPES)
        return self.current_move, self.current_shape, offset.x

    def find_period(self) -> Tuple[Tuple[int, int], List[int]]:
        seen: Dict[Tuple[int, int, int], List[Tuple[int, int]]] = defaultdict(list)
        round = 1
        while True:
            key = self.play_round()
            height = self.tallest_point
            if len(seen[key]) == 3:
                result: Tuple[Tuple[int, int], List[int]] = seen[key][1], []
                last_height = height
                period_key = key
                while period_key != self.play_round():
                    result[1].append(self.tallest_point - last_height)
                    last_height = self.tallest_point
                result[1].append(self.tallest_point - last_height)
                return result

            seen[key].append((round, height))
            round += 1

    def height_at_round(self, round: int) -> int:
        (start, height), gains = self.find_period()
        after_start = round - start
        full_rounds = after_start // len(gains)
        gains_per_round = sum(gains)
        remainder = after_start % len(gains)
        return height + (full_rounds * gains_per_round) + sum(gains[:remainder])


def part1(text: str) -> int | None:
    board = TetrisBoard.parse(text)
    return board.height_at_round(2022)


def part2(text: str) -> int | None:
    board = TetrisBoard.parse(text)
    return board.height_at_round(1_000_000_000_000)
