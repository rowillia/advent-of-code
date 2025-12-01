from dataclasses import dataclass
from enum import Enum
import re
from typing import Dict, List
from aoc.common.point import Point


MOVE_RE = re.compile(r"(\d+)([RL]|$)")


class Direction(Enum):
    UP = Point(0, -1)
    RIGHT = Point(1, 0)
    DOWN = Point(0, 1)
    LEFT = Point(-1, 0)

    def turn(self, direction: str) -> "Direction":
        directions = list(Direction)
        if direction == "":
            return self
        if direction == "L":
            return directions[(directions.index(self) - 1) % len(directions)]
        elif direction == "R":
            return directions[(directions.index(self) + 1) % len(directions)]
        raise Exception("Invalid Direction")


NET = [
    ["..2.", "651.", "..43", "....", "...."],
    [".6..", ".2..", "51..", "4...", "3..."],
]

CUBE_GRAPH = {
    1: {Direction.UP: (2, 1), Direction.RIGHT: (3, -1), Direction.RIGHT: (3, -1)}
}

DIRECTION_TO_CHAR = {
    Direction.UP: "^",
    Direction.RIGHT: ">",
    Direction.DOWN: "v",
    Direction.LEFT: "<",
}

DIRECTION_TO_VALUE = {
    Direction.UP: 3,
    Direction.RIGHT: 0,
    Direction.DOWN: 1,
    Direction.LEFT: 2,
}


@dataclass(frozen=True)
class Arrow:
    location: Point
    direction: Direction


@dataclass(frozen=True)
class Move:
    direction: str
    distance: int

    @classmethod
    def parse(cls, text: str) -> List["Move"]:
        result = []
        for match in MOVE_RE.finditer(text):
            distance, direction = match.groups()
            result.append(Move(direction, int(distance)))
        return result


@dataclass
class Maze:
    spaces: Dict[Point, bool]
    connections: Dict[Arrow, Point]
    start: Arrow
    bottom_right: Point
    moves: List[Move]

    @classmethod
    def parse(cls, text: str, part2: bool = False) -> "Maze":
        maze_text, path = text.split("\n\n")
        maze_lines = maze_text.splitlines()
        longest_line = max(len(line) for line in maze_lines)
        maze_lines.append(" " * longest_line)
        maze_lines = [line.ljust(longest_line + 1, " ") for line in maze_lines]
        spaces: Dict[Point, bool] = {}
        connections: Dict[Arrow, Point] = {}
        row_starts: Dict[int, Point] = {}
        col_starts: Dict[int, Point] = {}
        p = Point(0, 0)
        face_width = 500
        for y, row in enumerate(maze_lines):
            row_width = 0
            for x, val in enumerate(row):
                p = Point(x, y)
                if val == " ":
                    last_col = Point(x - 1, y)
                    last_row = Point(x, y - 1)
                    if last_col in spaces:
                        row_start = row_starts[y]
                        connections[Arrow(row_start, Direction.LEFT)] = last_col
                        connections[Arrow(last_col, Direction.RIGHT)] = row_start
                    if last_row in spaces:
                        col_start = col_starts[x]
                        connections[Arrow(col_start, Direction.UP)] = last_row
                        connections[Arrow(last_row, Direction.DOWN)] = col_start
                else:
                    if y not in row_starts:
                        row_starts[y] = p
                    if x not in col_starts:
                        col_starts[x] = p
                    spaces[p] = val == "."
                    row_width += 1
            if row_width < face_width:
                face_width = row_width
        start = Arrow(row_starts[0], Direction.RIGHT)
        return Maze(spaces, connections, start, p, Move.parse(path))

    def execute(self) -> List[Arrow]:
        pointer = self.start
        path = [pointer]
        for move in self.moves:
            for space in range(move.distance):
                next_space: Point = pointer.location + pointer.direction.value
                if next_space not in self.spaces:
                    next_space = self.connections[pointer]

                if self.spaces[next_space]:
                    pointer = Arrow(next_space, pointer.direction)
                    path.append(pointer)
            pointer = Arrow(pointer.location, pointer.direction.turn(move.direction))
            path[-1] = pointer
        return path

    def render(self, path: List[Arrow]) -> str:
        result = []
        path_points = {p.location: p for p in path}
        for y in range(self.bottom_right.y):
            line = []
            for x in range(self.bottom_right.x):
                p = Point(x, y)
                if p in path_points:
                    line.append(DIRECTION_TO_CHAR[path_points[p].direction])
                elif p not in self.spaces:
                    line.append(" ")
                else:
                    line.append("." if self.spaces[p] else "#")
            result.append("".join(line))
        return "\n".join(result)


def part1(text: str) -> int | None:
    m = Maze.parse(text)
    path = m.execute()
    end = path[-1]
    print(m.render(path))
    print(end)
    return (
        (1000 * (end.location.y + 1))
        + (4 * (end.location.x + 1))
        + DIRECTION_TO_VALUE[end.direction]
    )
