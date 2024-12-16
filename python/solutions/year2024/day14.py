"""
--- Day 14: Restroom Redoubt ---
One of The Historians needs to use the bathroom; fortunately, you know there's a
bathroom near an unvisited location on their list, and so you're all quickly
teleported directly to the lobby of Easter Bunny Headquarters.

Unfortunately, EBHQ seems to have "improved" bathroom security again after your
last visit. The area outside the bathroom is swarming with robots!

To get The Historian safely to the bathroom, you'll need a way to predict where
the robots will be in the future. Fortunately, they all seem to be moving on the
tile floor in predictable straight lines.

You make a list (your puzzle input) of all of the robots' current positions (p)
and velocities (v), one robot per line. For example:

p=0,4 v=3,-3
p=6,3 v=-1,-3
p=10,3 v=-1,2
p=2,0 v=2,-1
p=0,0 v=1,3
p=3,0 v=-2,-2
p=7,6 v=-1,-3
p=3,0 v=-1,-2
p=9,3 v=2,3
p=7,3 v=-1,2
p=2,4 v=2,-3
p=9,5 v=-3,-3

Each robot's position is given as p=x,y where x represents the number of tiles
the robot is from the left wall and y represents the number of tiles from the
top wall (when viewed from above). So, a position of p=0,0 means the robot is
all the way in the top-left corner.

Each robot's velocity is given as v=x,y where x and y are given in tiles per
second. Positive x means the robot is moving to the right, and positive y means
the robot is moving down. So, a velocity of v=1,-2 means that each second, the
robot moves 1 tile to the right and 2 tiles up.

The robots outside the actual bathroom are in a space which is 101 tiles wide
and 103 tiles tall (when viewed from above). However, in this example, the
robots are in a space which is only 11 tiles wide and 7 tiles tall.

The robots are good at navigating over/under each other (due to a combination of
springs, extendable legs, and quadcopters), so they can share the same tile and
don't interact with each other. Visually, the number of robots on each tile in
this example looks like this:

1.12.......
...........
...........
......11.11
1.1........
.........1.
.......1...

These robots have a unique feature for maximum bathroom security: they can
teleport. When a robot would run into an edge of the space they're in, they
instead teleport to the other side, effectively wrapping around the edges. Here
is what robot p=2,4 v=2,-3 does for the first few seconds:

Initial state:
...........
...........
...........
...........
..1........
...........
...........

After 1 second:
...........
....1......
...........
...........
...........
...........
...........

After 2 seconds:
...........
...........
...........
...........
...........
......1....
...........

After 3 seconds:
...........
...........
........1..
...........
...........
...........
...........

After 4 seconds:
...........
...........
...........
...........
...........
...........
..........1

After 5 seconds:
...........
...........
...........
.1.........
...........
...........
...........

The Historian can't wait much longer, so you don't have to simulate the robots
for very long. Where will the robots be after 100 seconds?

In the above example, the number of robots on each tile after 100 seconds has
elapsed looks like this:

......2..1.
...........
1..........
.11........
.....1.....
...12......
.1....1....

To determine the safest area, count the number of robots in each quadrant after
100 seconds. Robots that are exactly in the middle (horizontally or vertically)
don't count as being in any quadrant, so the only relevant robots are:

..... 2..1.
..... .....
1.... .....

..... .....
...12 .....
.1... 1....

In this example, the quadrants contain 1, 3, 4, and 1 robot. Multiplying these
together gives a total safety factor of 12.

Predict the motion of the robots in your list within a space which is 101 tiles
wide and 103 tiles tall. What will the safety factor be after exactly 100
seconds have elapsed?
"""

import re
from collections import defaultdict
from dataclasses import dataclass
from functools import reduce
from typing import Counter

from python.common.point import Point

DRONE_LINE = re.compile(r"p=(-?\d+),(-?\d+) v=(-?\d+),(-?\d+)")


@dataclass(frozen=True)
class Drone:
    position: Point
    velocity: Point

    @classmethod
    def parse(cls, line: str):
        if match := DRONE_LINE.match(line):
            pos_x, pos_y, vel_x, vel_y = map(int, match.groups())
            return Drone(Point(pos_x, pos_y), Point(vel_x, vel_y))
        raise Exception(f"Invalid line {line}")

    def next(self, upper_bound: Point):
        new_pos = self.position + self.velocity
        new_pos = Point(new_pos.x % upper_bound.x, new_pos.y % upper_bound.y)
        return Drone(new_pos, self.velocity)

    def in_bucket(self, lower_bound: Point, upper_bound: Point):
        if (
            lower_bound.x <= self.position.x < upper_bound.x
            and lower_bound.y <= self.position.y < upper_bound.y
        ):
            return True
        return False


@dataclass(frozen=True)
class Room:
    drones: tuple[Drone, ...]
    bound: Point

    @classmethod
    def parse(cls, text: str):
        drones = [Drone.parse(line) for line in text.splitlines()]
        return Room(
            tuple(drones),
            Point(
                max(d.position.x for d in drones) + 1,
                max(d.position.y for d in drones) + 1,
            ),
        )

    def next(self):
        new_drones = [d.next(self.bound) for d in self.drones]
        return Room(tuple(new_drones), self.bound)

    def __str__(self):
        result = []
        positions = Counter([d.position for d in self.drones])
        for row in range(self.bound.y):
            current = []
            for col in range(self.bound.x):
                if Point(col, row) in positions:
                    current.append(str(positions[Point(col, row)]))
                else:
                    current.append(".")
            result.append("".join(current))
        return "\n".join(result)

    def horizontal_lines(self, min_length: int = 3):
        drones_to_row = defaultdict(list)
        for drone in self.drones:
            drones_to_row[drone.position.y].append(drone.position.x)
        for row in drones_to_row.values():
            row.sort()
        total = 0
        for row in drones_to_row.values():
            current_run = 0
            last_col = None
            for col in row:
                if last_col == col - 1:
                    current_run += 1
                elif last_col == col:
                    continue
                else:
                    if current_run >= min_length:
                        total += 1
                    current_run = 1
                last_col = col
            if current_run >= min_length:
                total += 1
        return total

    @property
    def buckets(self):
        lower_x_upper = self.bound.x // 2
        right_x_lower = self.bound.x - (self.bound.x // 2)
        top_y_upper = self.bound.y // 2
        bottom_y_lower = self.bound.y - (self.bound.y // 2)
        buckets = {
            (Point(0, 0), Point(lower_x_upper, top_y_upper)): 0,
            (Point(right_x_lower, 0), Point(self.bound.x, top_y_upper)): 0,
            (
                Point(0, bottom_y_lower),
                Point(lower_x_upper, self.bound.y),
            ): 0,
            (
                Point(right_x_lower, bottom_y_lower),
                Point(self.bound.x, self.bound.y),
            ): 0,
        }
        for drone in self.drones:
            for bounds in buckets:
                if drone.in_bucket(*bounds):
                    buckets[bounds] += 1
        return buckets

    @property
    def score(self):
        return reduce(lambda x, y: x * y, self.buckets.values(), 1)


def part1(text: str) -> int | None:
    room = Room.parse(text)
    for _ in range(100):
        room = room.next()
    return room.score


def part2(text: str) -> str | None:
    room = Room.parse(text)
    for idx in range(1, 100_000):
        room = room.next()
        if room.horizontal_lines(5) > 10:
            print(f"Version {idx}:")
            print("==========")
            print(str(room))
            print("==========")
            break
