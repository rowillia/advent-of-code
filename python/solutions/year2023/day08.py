import math
from dataclasses import dataclass
from itertools import cycle
import re
from typing import Iterable


NODE_LINE_RE = re.compile(r"(\w+)\s+=\s+\((\w+),\s+(\w+)\)")


def lcm(numbers: Iterable[int]) -> int:
    lcm = 1
    for n in numbers:
        lcm = lcm * n // math.gcd(lcm, n)
    return lcm


def iterlen(iterable: Iterable) -> int:
    return sum(1 for _ in iterable)


@dataclass(frozen=True)
class Network:
    turns: list[bool]
    nodes: dict[str, tuple[str, str]]

    @classmethod
    def parse(cls, text: str) -> "Network":
        lines = text.splitlines()
        turns = [x == "R" for x in lines[0]]

        nodes = {}
        for line in lines[2:]:
            if match := NODE_LINE_RE.match(line):
                node, left, right = match.groups()
                nodes[node] = (left, right)
            else:
                raise ValueError(f"Invalid line: {line}")
        return Network(turns, nodes)

    def run(self, start: str = "AAA", end: str = "ZZZ") -> Iterable[str]:
        instructions = cycle(self.turns)
        current = start
        while not current.endswith(end):
            turn = next(instructions)
            current = self.nodes[current][int(turn)]
            yield current

    def ghost_run(self) -> int:
        starts = [node for node in self.nodes if node.endswith("A")]
        periods = [iterlen(self.run(start, "Z")) for start in starts]
        return lcm(periods)


def part1(text: str) -> int | None:
    return len(list(Network.parse(text).run()))


def part2(text: str) -> int | None:
    n = Network.parse(text)
    return n.ghost_run()
