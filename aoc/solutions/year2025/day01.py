"""
--- Day 1: Secret Entrance ---
"""

from dataclasses import dataclass

year = 2025
day = 1

STARTING_POSITION = 50


@dataclass(frozen=True)
class Rotation:
    direction: str
    count: int

    @classmethod
    def parse(cls, command: str):
        return Rotation(command[0], int(command[1:]))

    def apply(self, position: int):
        if self.direction == "R":
            new_pos = position + self.count % 100
        else:
            new_pos = position - self.count % 100
        passes = self.count // 100
        if new_pos >= 100:
            passes += 1
        if position > 0 and new_pos <= 0:
            passes += 1
        return new_pos % 100, passes


# %%
def part1(text: str) -> int | None:
    current = STARTING_POSITION
    total = 0
    for rot in (Rotation.parse(x) for x in text.splitlines()):
        new_pos, _ = rot.apply(current)
        if new_pos == 0:
            total += 1
        current = new_pos
    return total


# %%
def part2(text: str) -> int | None:
    current = STARTING_POSITION
    total = 0
    rotations = [Rotation.parse(x) for x in text.splitlines()]
    for rot in rotations:
        new_pos, passes = rot.apply(current)
        total += passes
        current = new_pos
    return total
