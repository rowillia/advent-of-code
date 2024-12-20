"""
--- Day 16: Reindeer Maze ---
It's time again for the Reindeer Olympics! This year, the big event is the
Reindeer Maze, where the Reindeer compete for the lowest score.

You and The Historians arrive to search for the Chief right as the event is
about to start. It wouldn't hurt to watch a little, right?

The Reindeer start on the Start Tile (marked S) facing East and need to reach
the End Tile (marked E). They can move forward one tile at a time (increasing
their score by 1 point), but never into a wall (#). They can also rotate
clockwise or counterclockwise 90 degrees at a time (increasing their score by
1000 points).

To figure out the best place to sit, you start by grabbing a map (your puzzle
input) from a nearby kiosk. For example:

###############
#.......#....E#
#.#.###.#.###.#
#.....#.#...#.#
#.###.#####.#.#
#.#.#.......#.#
#.#.#####.###.#
#...........#.#
###.#.#####.#.#
#...#.....#.#.#
#.#.#.###.#.#.#
#.....#...#.#.#
#.###.#.#.#.#.#
#S..#.....#...#
###############

There are many paths through this maze, but taking any of the best paths would
incur a score of only 7036. This can be achieved by taking a total of 36 steps
forward and turning 90 degrees a total of 7 times:


###############
#.......#....E#
#.#.###.#.###^#
#.....#.#...#^#
#.###.#####.#^#
#.#.#.......#^#
#.#.#####.###^#
#..>>>>>>>>v#^#
###^#.#####v#^#
#>>^#.....#v#^#
#^#.#.###.#v#^#
#^....#...#v#^#
#^###.#.#.#v#^#
#S..#.....#>>^#
###############

Here's a second example:

#################
#...#...#...#..E#
#.#.#.#.#.#.#.#.#
#.#.#.#...#...#.#
#.#.#.#.###.#.#.#
#...#.#.#.....#.#
#.#.#.#.#.#####.#
#.#...#.#.#.....#
#.#.#####.#.###.#
#.#.#.......#...#
#.#.###.#####.###
#.#.#...#.....#.#
#.#.#.#####.###.#
#.#.#.........#.#
#.#.#.#########.#
#S#.............#
#################

In this maze, the best paths cost 11048 points; following one such path would
look like this:

#################
#...#...#...#..E#
#.#.#.#.#.#.#.#^#
#.#.#.#...#...#^#
#.#.#.#.###.#.#^#
#>>v#.#.#.....#^#
#^#v#.#.#.#####^#
#^#v..#.#.#>>>>^#
#^#v#####.#^###.#
#^#v#..>>>>^#...#
#^#v###^#####.###
#^#v#>>^#.....#.#
#^#v#^#####.###.#
#^#v#^........#.#
#^#v#^#########.#
#S#>>^..........#
#################

Note that the path shown above includes one 90 degree turn as the very first
move, rotating the Reindeer from facing East to facing North.

Analyze your map carefully. What is the lowest score a Reindeer could possibly
get?
"""

from dataclasses import dataclass

from python.common.astar import astar_with_cost
from python.common.grid import Grid
from python.common.point import Point

EAST = Point(1, 0)


def sign(x):
    return (x > 0) - (x < 0)


@dataclass(frozen=True)
class Reindeer:
    loc: Point
    direction: Point


class Goal(Reindeer):
    def __eq__(self, value):
        if isinstance(value, Reindeer):
            return value.loc == self.loc
        return super().__eq__(value)

    def __hash__(self):
        return hash(self.loc)


class Maze(Grid[str]):
    def solve(self):
        start = [key for key, value in self.entries.items() if value == "S"][0]
        end = [key for key, value in self.entries.items() if value == "E"][0]

        def neighbors(reindeer: Reindeer):
            result: list[tuple[Reindeer, int]] = []
            moves = [
                (reindeer.direction.rotate_left(), 0, 1000),
                (reindeer.direction, 1, 1),
                (reindeer.direction.rotate_right(), 0, 1000),
            ]
            for direction, move, cost in moves:
                if self.entries[reindeer.loc + direction] != "#":
                    result.append(
                        (Reindeer(reindeer.loc + (direction * move), direction), cost)
                    )

            return result

        def heuristic(r1: Reindeer, r2: Reindeer) -> int:
            delta = r1.loc - r2.loc
            if sign(delta.x) != r1.direction.x or sign(delta.y) != r1.direction.y:
                turn_cost = 1000
            else:
                turn_cost = 1
            return r1.loc.manhattan_distance(r2.loc) + turn_cost

        _, cost = astar_with_cost(
            Reindeer(start, EAST), Goal(end, EAST), heuristic, neighbors
        )
        return cost


def part1(text: str) -> int | None:
    return Maze.parse(text, str).solve()


def part2(text: str) -> str | None:
    return None
