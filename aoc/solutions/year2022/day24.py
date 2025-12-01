from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from functools import cache, cached_property
from typing import Dict, Iterable, List, Tuple

import immutables

from aoc.common.graph import astar_optimizable
from aoc.common.point import Point


class Direction(Enum):
    UP = Point(0, -1)
    RIGHT = Point(1, 0)
    DOWN = Point(0, 1)
    LEFT = Point(-1, 0)


DIRECTION_TO_CHAR = {
    Direction.UP: "^",
    Direction.RIGHT: ">",
    Direction.DOWN: "v",
    Direction.LEFT: "<",
}


CHAR_TO_DIRECTION = {c: d for d, c in DIRECTION_TO_CHAR.items()}


@dataclass(frozen=True)
class Maze:
    start: Point
    end: Point
    top_left: Point
    bottom_right: Point

    @cached_property
    def _hash(self) -> int:
        return hash((self.start, self.end, self.top_left, self.bottom_right))

    def __hash__(self) -> int:
        return self._hash

    def __contains__(self, point: Point) -> bool:
        return (
            point == self.start
            or point == self.end
            or (0 < point.x < self.bottom_right.x and 0 < point.y < self.bottom_right.y)
        )


@cache
def progress_blizzards(
    prior_blizzards: immutables.Map[Point, Tuple[Direction, ...]], maze: Maze
) -> immutables.Map[Point, Tuple[Direction, ...]]:
    blizzards: Dict[Point, List[Direction]] = defaultdict(list)
    for position, directions in prior_blizzards.items():
        for direction in directions:
            next_point = position + direction.value
            if next_point.x >= maze.bottom_right.x:
                next_point = Point(1, next_point.y)
            if next_point.y >= maze.bottom_right.y:
                next_point = Point(next_point.x, 1)
            if next_point.x <= 0:
                next_point = Point(maze.bottom_right.x - 1, next_point.y)
            if next_point.y <= 0:
                next_point = Point(next_point.x, maze.bottom_right.y - 1)
            blizzards[next_point].append(direction)
    return immutables.Map([(p, tuple(d)) for p, d in blizzards.items()])


@dataclass(frozen=True)
class State:
    blizzards: immutables.Map[Point, Tuple[Direction, ...]]
    position: Point
    maze: Maze

    @cached_property
    def is_valid(self) -> bool:
        return (self.position in self.maze) and (self.position not in self.blizzards)

    @cached_property
    def is_finished(self) -> bool:
        return self.position == self.maze.end

    @cached_property
    def heuristic(self) -> int:
        return self.position.manhattan_distance(self.maze.end)

    @cached_property
    def next(self) -> "State":
        return State(
            progress_blizzards(self.blizzards, self.maze),
            self.position,
            self.maze,
        )

    def egress(self) -> Iterable[Tuple["State", int]]:
        next_state = self.next
        if next_state.is_valid:
            yield next_state, 1
        for direction in Direction:
            potential_position = State(
                next_state.blizzards, self.position + direction.value, self.maze
            )
            if potential_position.is_valid:
                yield potential_position, 1

    @classmethod
    def parse(cls, text: str) -> "State":
        lines = text.splitlines()
        top_left = Point(0, 0)
        bottom_right = Point(len(lines[0]) - 1, len(lines) - 1)
        start: Point | None = None
        end: Point | None = None
        blizzards: Dict[Point, List[Direction]] = defaultdict(list)
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                p = Point(x, y)
                if char == ".":
                    if y == 0:
                        start = p
                    elif y == len(lines) - 1:
                        end = p
                if char in CHAR_TO_DIRECTION:
                    blizzards[p].append(CHAR_TO_DIRECTION[char])
        assert start is not None and end is not None
        maze = Maze(
            start,
            end,
            top_left,
            bottom_right,
        )
        return State(
            immutables.Map([(p, tuple(d)) for p, d in blizzards.items()]), start, maze
        )

    def __str__(self) -> str:
        result = []
        for y in range(self.maze.bottom_right.y + 1):
            line = []
            for x in range(self.maze.bottom_right.x + 1):
                p = Point(x, y)
                if p == self.position:
                    line.append("@")
                elif (
                    x == 0
                    or y == 0
                    or x == self.maze.bottom_right.x
                    or y == self.maze.bottom_right.y
                ) and (p != self.maze.start and p != self.maze.end):
                    line.append("#")
                elif p in self.blizzards:
                    if len(self.blizzards[p]) > 1:
                        line.append(str(len(self.blizzards[p])))
                    else:
                        line.append(DIRECTION_TO_CHAR[self.blizzards[p][0]])
                else:
                    line.append(".")
            result.append("".join(line))
        return "\n".join(result)


def part1(text: str) -> int | None:
    m = State.parse(text)
    path: List[State] = astar_optimizable(m)[0]
    return len(path) - 1


def part2(text: str) -> int | None:
    m = State.parse(text)
    path: List[State] = astar_optimizable(m)[0]  # type: ignore
    first_half = len(path) - 1
    m = State(
        path[-1].blizzards,
        path[-1].position,
        Maze(m.maze.end, m.maze.start, m.maze.top_left, m.maze.bottom_right),
    )
    path = astar_optimizable(m)[0]
    go_back = len(path) - 1
    m = State(
        path[-1].blizzards,
        path[-1].position,
        Maze(m.maze.end, m.maze.start, m.maze.top_left, m.maze.bottom_right),
    )
    path = astar_optimizable(m)[0]
    return first_half + go_back + len(path) - 1
