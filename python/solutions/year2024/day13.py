"""
--- Day 13: Claw Contraption ---
Next up: the lobby of a resort on a tropical island. The Historians take a
moment to admire the hexagonal floor tiles before spreading out.

Fortunately, it looks like the resort has a new arcade! Maybe you can win some
prizes from the claw machines?

The claw machines here are a little unusual. Instead of a joystick or
directional buttons to control the claw, these machines have two buttons labeled
A and B. Worse, you can't just put in a token and play; it costs 3 tokens to
push the A button and 1 token to push the B button.

With a little experimentation, you figure out that each machine's buttons are
configured to move the claw a specific amount to the right (along the X axis)
and a specific amount forward (along the Y axis) each time that button is
pressed.

Each machine contains one prize; to win the prize, the claw must be positioned
exactly above the prize on both the X and Y axes.

You wonder: what is the smallest number of tokens you would have to spend to win
as many prizes as possible? You assemble a list of every machine's button
behavior and prize location (your puzzle input). For example:

Button A: X+94, Y+34
Button B: X+22, Y+67
Prize: X=8400, Y=5400

Button A: X+26, Y+66
Button B: X+67, Y+21
Prize: X=12748, Y=12176

Button A: X+17, Y+86
Button B: X+84, Y+37
Prize: X=7870, Y=6450

Button A: X+69, Y+23
Button B: X+27, Y+71
Prize: X=18641, Y=10279

This list describes the button configuration and prize location of four
different claw machines.

For now, consider just the first claw machine in the list:


  * Pushing the machine's A button would move the claw 94 units along the X axis
and 34 units along the Y axis.
  * Pushing the B button would move the claw 22 units along the X axis and 67
units along the Y axis.
  * The prize is located at X=8400, Y=5400; this means that from the claw's
initial position, it would need to move exactly 8400 units along the X axis and
exactly 5400 units along the Y axis to be perfectly aligned with the prize in
this machine.

The cheapest way to win the prize is by pushing the A button 80 times and the B
button 40 times. This would line up the claw along the X axis (because 80*94 +
40*22 = 8400) and along the Y axis (because 80*34 + 40*67 = 5400). Doing this
would cost 80*3 tokens for the A presses and 40*1 for the B presses, a total of
280 tokens.

For the second and fourth claw machines, there is no combination of A and B
presses that will ever win a prize.

For the third claw machine, the cheapest way to win the prize is by pushing the
A button 38 times and the B button 86 times. Doing this would cost a total of
200 tokens.

So, the most prizes you could possibly win is two; the minimum tokens you would
have to spend to win all (two) prizes is 480.

You estimate that each button would need to be pressed no more than 100 times to
win a prize. How else would someone be expected to play?

Figure out how to win as many prizes as possible. What is the fewest tokens you
would have to spend to win all possible prizes?
"""

import re
from dataclasses import dataclass

import numpy as np

from python.common.point import Point

BUTTON_RE = re.compile(r"Button [AB]: X\+(\d+), Y\+(\d+)")
PRIZE_RE = re.compile(r"Prize: X=(\d+), Y=(\d+)")
A_COST = 3
B_COST = 1


@dataclass(frozen=True)
class ClawGame:
    a: Point
    b: Point
    prize: Point

    @classmethod
    def parse(cls, text: str, part2: bool = False):
        lines = text.splitlines()
        prize_offset = Point(0, 0)
        if part2:
            prize_offset = Point(10_000_000_000_000, 10_000_000_000_000)
        if (a_match := BUTTON_RE.match(lines[0])) is None:
            raise Exception(f"Invalid button: {lines[0]}")
        if (b_match := BUTTON_RE.match(lines[1])) is None:
            raise Exception(f"Invalid button: {lines[1]}")
        if (prize_match := PRIZE_RE.match(lines[2])) is None:
            raise Exception(f"Invalid prize: {lines[2]}")
        a = Point(*[int(val) for val in a_match.groups()])
        b = Point(*[int(val) for val in b_match.groups()])
        prize = Point(*[int(val) for val in prize_match.groups()])
        return cls(a, b, prize + prize_offset)

    def min_cost_to_prize(self):
        lhs = np.array([[self.a.x, self.b.x], [self.a.y, self.b.y]]).astype(np.float64)
        rhs = np.array([self.prize.x, self.prize.y]).astype(np.float64)
        a_count, b_count = map(int, np.rint(np.linalg.solve(lhs, rhs)))
        if (a_count * self.a.x + b_count * self.b.x == self.prize.x) and (
            a_count * self.a.y + b_count * self.b.y == self.prize.y
        ):
            return a_count * A_COST + b_count * B_COST
        return 0


def part1(text: str) -> int | None:
    games = text.split("\n\n")
    return sum(
        int(ClawGame.parse(game, part2=False).min_cost_to_prize()) for game in games
    )


def part2(text: str) -> int | None:
    games = text.split("\n\n")
    return sum(
        int(ClawGame.parse(game, part2=True).min_cost_to_prize()) for game in games
    )
