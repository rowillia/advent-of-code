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

--- Part Two ---
Now that you know what the best paths look like, you can figure out the best
spot to sit.

Every non-wall tile (S, ., or E) is equipped with places to sit along the edges
of the tile. While determining which of these tiles would be the best spot to
sit depends on a whole bunch of factors (how comfortable the seats are, how far
away the bathrooms are, whether there's a pillar blocking your view, etc.), the
most important factor is whether the tile is on one of the best paths through
the maze. If you sit somewhere else, you'd miss all the action!

So, you'll need to determine which tiles are part of any best path through the
maze, including the S and E tiles.

In the first example, there are 45 tiles (marked O) that are part of at least
one of the various best paths through the maze:

###############
#.......#....O#
#.#.###.#.###O#
#.....#.#...#O#
#.###.#####.#O#
#.#.#.......#O#
#.#.#####.###O#
#..OOOOOOOOO#O#
###O#O#####O#O#
#OOO#O....#O#O#
#O#O#O###.#O#O#
#OOOOO#...#O#O#
#O###.#.#.#O#O#
#O..#.....#OOO#
###############

In the second example, there are 64 tiles that are part of at least one of the
best paths:

#################
#...#...#...#..O#
#.#.#.#.#.#.#.#O#
#.#.#.#...#...#O#
#.#.#.#.###.#.#O#
#OOO#.#.#.....#O#
#O#O#.#.#.#####O#
#O#O..#.#.#OOOOO#
#O#O#####.#O###O#
#O#O#..OOOOO#OOO#
#O#O###O#####O###
#O#O#OOO#..OOO#.#
#O#O#O#####O###.#
#O#O#OOOOOOO..#.#
#O#O#O#########.#
#O#OOO..........#
#################

Analyze your map further. How many tiles are part of at least one of the best
paths through the maze?
"""

from dataclasses import dataclass

from python.common.graph import astar_with_cost
from python.common.grid import Grid
from python.common.point import Point
from python.common.priority_queue import PriorityQueue

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
    def neighbors(self, reindeer: Reindeer):
        result: list[tuple[Reindeer, int]] = []
        turn_penalty = 1000
        if isinstance(reindeer, Goal):
            turn_penalty = 0
        moves = [
            (reindeer.direction.rotate_left(), 0, turn_penalty),
            (reindeer.direction, 1, 1),
            (reindeer.direction.rotate_right(), 0, turn_penalty),
        ]
        for direction, move, cost in moves:
            if self.entries[reindeer.loc + direction] != "#":
                result.append(
                    (Reindeer(reindeer.loc + (direction * move), direction), cost)
                )

        return result

    @staticmethod
    def heuristic(r1: Reindeer, r2: Reindeer) -> int:
        delta = r1.loc - r2.loc
        if sign(delta.x) != r1.direction.x or sign(delta.y) != r1.direction.y:
            turn_cost = 1000
        else:
            turn_cost = 0
        return r1.loc.manhattan_distance(r2.loc) + turn_cost

    def solve(self):
        start = [key for key, value in self.entries.items() if value == "S"][0]
        end = [key for key, value in self.entries.items() if value == "E"][0]

        _, cost = astar_with_cost(
            Reindeer(start, EAST), Goal(end, EAST), self.heuristic, self.neighbors
        )
        return cost

    def all_paths(self):
        start = [key for key, value in self.entries.items() if value == "S"][0]
        end = [key for key, value in self.entries.items() if value == "E"][0]

        path, best_cost = astar_with_cost(
            Reindeer(start, EAST), Goal(end, EAST), self.heuristic, self.neighbors
        )
        in_best = set()
        frontier: PriorityQueue[Reindeer] = PriorityQueue()
        frontier.push(path[0], 0)
        solved_costs = {path[0]: best_cost}
        for current, last in zip(path[1:], path):
            solved_costs[current] = solved_costs[last] - self.heuristic(current, last)

        while frontier:
            node, cost_to_node = frontier.pop_with_priorty()
            for neighbor, cost in self.neighbors(node):
                if neighbor in solved_costs:
                    cost_to_end = solved_costs[neighbor]
                    my_path = None
                else:
                    try:
                        my_path, cost_to_end = astar_with_cost(
                            neighbor, Goal(end, EAST), self.heuristic, self.neighbors
                        )
                    except Exception:
                        continue
                total_cost = cost_to_end + cost_to_node + cost
                if total_cost == best_cost:
                    if my_path:
                        for current, last in zip(path[1:], path):
                            solved_costs[current] = solved_costs[last] - self.heuristic(
                                current, last
                            )
                    if neighbor not in in_best:
                        frontier.push(neighbor, cost_to_node + cost)

            in_best.add(node)
        return len({r.loc for r in in_best})


def part1(text: str) -> int | None:
    return Maze.parse(text, str).solve()


def part2(text: str) -> int | None:
    return Maze.parse(text, str).all_paths()
