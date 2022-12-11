from itertools import islice
import math
import re
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Iterator, List


TEST_LINE_RE = re.compile(r"Test: divisible by (\d+)")
RESULT_LINE_RE = re.compile(r"If \w+: throw to monkey (\d+)")
MONKEY_ID_RE = re.compile(r"Monkey (\d+):")
STARTING_ITEMS_RE = re.compile(r"Starting items: ([\d\s,]+)")
OPERATION_RE = re.compile(r"Operation: new = (\d+|old) ([+*]) (\d+|old)")


@dataclass
class Test:
    divisble: int
    true_target: int
    false_target: int

    @classmethod
    def parse(cls, text: Iterable[str]) -> "Test":
        test, true_line, false_line = (x.strip() for x in islice(text, 3))
        test_match = TEST_LINE_RE.match(test)
        true_match = RESULT_LINE_RE.match(true_line)
        false_match = RESULT_LINE_RE.match(false_line)
        if test_match and true_match and false_match:
            return Test(
                int(test_match.group(1)),
                int(true_match.group(1)),
                int(false_match.group(1)),
            )
        raise Exception("Invalid test")

    def evaluate(self, worry: int) -> int:
        if worry % self.divisble == 0:
            return self.true_target
        return self.false_target


@dataclass
class Operation:
    operator: Callable[[int, int], int]
    lhs: int | str
    rhs: int | str

    @classmethod
    def parse(cls, text: Iterator[str]) -> "Operation":
        operation_line = next(text, "").strip()
        if operation_match := OPERATION_RE.match(operation_line):
            lhs = operation_match.group(1)
            rhs = operation_match.group(3)
            return Operation(
                int.__add__ if operation_match.group(2) == "+" else int.__mul__,
                int(lhs) if lhs.isnumeric() else lhs,
                int(rhs) if rhs.isnumeric() else rhs,
            )
        raise Exception("Invalid Operation")

    def evaluate(self, old: int) -> int:
        lhs = self.lhs if isinstance(self.lhs, int) else old
        rhs = self.rhs if isinstance(self.rhs, int) else old
        return self.operator(lhs, rhs)


@dataclass
class Throw:
    item: int
    to: int


@dataclass
class Monkey:
    mid: int
    items: List[int]
    operation: Operation
    test: Test
    inspection_count: int = 0

    @classmethod
    def parse(cls, text: Iterator[str]) -> "Monkey":
        id_line, starting_line = (x.strip() for x in islice(text, 2))
        id_match = MONKEY_ID_RE.match(id_line)
        starting_match = STARTING_ITEMS_RE.match(starting_line)
        operation = Operation.parse(text)
        test = Test.parse(text)
        if id_match and starting_match:
            return Monkey(
                int(id_match.group(1)),
                [int(x) for x in starting_match.group(1).split(", ")],
                operation,
                test,
            )
        raise Exception("Invalid Monkey Configuration")

    def evaluate(self, lcm: int | None = None) -> List[Throw]:
        result = []
        for item in self.items:
            worry = self.operation.evaluate(item)
            if lcm:
                worry %= lcm
            else:
                worry //= 3
            result.append(Throw(worry, self.test.evaluate(worry)))
            self.inspection_count += 1
        self.items.clear()
        return result


@dataclass
class Game:
    monkeys: Dict[int, Monkey]

    def play_round(self, lcm: int | None = None) -> None:
        for mid in range(len(self.monkeys)):
            for throw in self.monkeys[mid].evaluate(lcm):
                self.monkeys[throw.to].items.append(throw.item)

    @classmethod
    def parse(cls, text: str) -> "Game":
        monkeys = [Monkey.parse(iter(x.splitlines())) for x in text.split("\n\n")]
        return Game({m.mid: m for m in monkeys})


def part1(text: str) -> int | None:
    game = Game.parse(text)
    for _ in range(20):
        game.play_round()
    return math.prod(sorted([x.inspection_count for x in game.monkeys.values()])[-2:])


def part2(text: str) -> int | None:
    game = Game.parse(text)
    lcm = math.prod([x.test.divisble for x in game.monkeys.values()])
    for _ in range(10000):
        game.play_round(lcm)
    return math.prod(sorted([x.inspection_count for x in game.monkeys.values()])[-2:])
