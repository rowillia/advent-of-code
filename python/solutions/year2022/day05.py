from collections import defaultdict
from dataclasses import dataclass
import re
from typing import DefaultDict, List


MOVE_RE = re.compile(r"move (\d+) from (\d+) to (\d+)")


@dataclass
class Move:
    count: int
    origin: int
    dest: int


@dataclass
class SupplyStacks:
    stacks: List[List[str]]
    moves: List[Move]

    def process_moves(self, single_move: bool = True) -> str:
        for move in self.moves:
            moved = self.stacks[move.origin][-move.count :]
            self.stacks[move.origin] = self.stacks[move.origin][: -move.count]
            if single_move:
                self.stacks[move.dest].extend(reversed(moved))
            else:
                self.stacks[move.dest].extend(moved)
        return self.answer

    @property
    def answer(self) -> str:
        return "".join(x[-1] for x in self.stacks)


def parse_input(text: str) -> SupplyStacks:
    stacks: DefaultDict[int, List[str]] = defaultdict(list)
    moves: List[Move] = []
    lines = iter(text.splitlines())
    for line in lines:
        line = line.rstrip()
        if not line:
            break
        for match in re.finditer("[A-Z]", line):
            stacks[match.start() // 4].append(match.group())

    for line in lines:
        line = line.strip()
        if move_match := MOVE_RE.match(line):
            count, origin, dest = move_match.groups()
            moves.append(Move(int(count), int(origin) - 1, int(dest) - 1))

    return SupplyStacks([list(reversed(stacks[x])) for x in range(len(stacks))], moves)


def part1(text: str) -> str | None:
    return parse_input(text).process_moves()


def part2(text: str) -> str | None:
    return parse_input(text).process_moves(single_move=False)
