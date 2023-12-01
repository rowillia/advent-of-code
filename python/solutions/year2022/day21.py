import abc
from dataclasses import dataclass
from functools import cache
import re
from typing import Iterator

import immutables


NUMBER_MONKEY_RE = re.compile(r"(\w+): (\d+)")
OPERATOR_MONKEY_RE = re.compile(r"(\w+): (\w+) ([\+\-\*\/]) (\w+)")
OPERATORS = {
    "+": int.__add__,
    "-": int.__sub__,
    "*": int.__mul__,
    "/": int.__floordiv__,
    "==": int.__eq__,
}

INVERTED_OPERATOR = {
    "+": "-",
    "-": "+",
    "/": "*",
    "*": "/",
}


def id_generator() -> Iterator[int]:
    yield from range(1000000)


_id_generator = id_generator()


def gen_id() -> int:
    return next(_id_generator)


@dataclass(frozen=True)
class Monkey(abc.ABC):
    name: str

    @abc.abstractmethod
    def value(self, monkeys: immutables.Map[str, "Monkey"]) -> "Monkey":
        pass

    @classmethod
    def parse(cls, text: str, is_part2: bool = False) -> "Monkey":
        if NUMBER_MONKEY_RE.match(text):
            return NumberMonkey.parse(text, is_part2)
        return OperatorMonkey.parse(text, is_part2)


@dataclass(frozen=True)
class NumberMonkey(Monkey):
    number: int

    def __str__(self) -> str:
        return str(self.number)

    @cache
    def value(self, monkeys: immutables.Map[str, "Monkey"]) -> "Monkey":
        return self

    @classmethod
    def parse(cls, text: str, is_part2: bool = False) -> "Monkey":
        if match := NUMBER_MONKEY_RE.match(text):
            name, number = match.groups()
            if is_part2 and name == "humn":
                return Human(name)
            return NumberMonkey(name, int(number))
        raise Exception("Invalid number monkey")


NEG_1 = NumberMonkey("_neg1", -1)
ONE = NumberMonkey("_one", 1)


@dataclass(frozen=True)
class OperatorMonkey(Monkey):
    operator: str
    lhs: str
    rhs: str

    @cache
    def value(self, monkeys: immutables.Map[str, "Monkey"]) -> Monkey:
        lhs = monkeys[self.lhs].value(monkeys)
        rhs = monkeys[self.rhs].value(monkeys)
        if isinstance(lhs, NumberMonkey) and isinstance(rhs, NumberMonkey):
            return NumberMonkey(
                self.name, OPERATORS[self.operator](lhs.number, rhs.number)
            )
        return Human(
            f"humn-{gen_id()}",
            f"({lhs} {self.operator} {rhs})",
            self.operator,
            lhs,
            rhs,
        )

    @classmethod
    def parse(cls, text: str, is_part2: bool = False) -> "OperatorMonkey":
        if match := OPERATOR_MONKEY_RE.match(text):
            name, lhs, operator_text, rhs = match.groups()
            if is_part2 and name == "root":
                operator_text = "=="
            return OperatorMonkey(name, operator_text, lhs, rhs)
        raise Exception("Invalid operator monkey")


@dataclass(frozen=True)
class Human(Monkey):
    text: str = "humn"
    operator: str | None = None
    lhs: Monkey | None = None
    rhs: Monkey | None = None

    def __str__(self) -> str:
        return self.text

    @cache
    def value(self, monkeys: immutables.Map[str, "Monkey"]) -> Monkey:
        return self

    @classmethod
    def parse(cls, text: str, is_part2: bool = False) -> "Human":
        return Human("humn")

    def unwind(self, monkeys: immutables.Map[str, "Monkey"]) -> int:
        assert self.operator == "=="
        assert self.lhs is not None
        assert self.rhs is not None

        lhs = self.lhs.value(monkeys)
        rhs = self.rhs.value(monkeys)

        lhs = self.lhs if isinstance(self.lhs, Human) else self.rhs
        assert isinstance(lhs, Human)
        rhs = self.rhs if isinstance(self.rhs, NumberMonkey) else self.lhs
        assert isinstance(rhs, NumberMonkey)

        operator = lhs.operator

        if operator is None:
            return rhs.number

        assert lhs.lhs is not None
        assert lhs.rhs is not None

        lhs_lhs = lhs.lhs
        lhs_rhs = lhs.rhs

        if isinstance(lhs_rhs, Human):
            if operator == "+" or operator == "*":
                lhs_lhs, lhs_rhs = lhs.rhs, lhs.lhs
            elif operator == "-":
                lhs_lhs = Human(f"humn-{gen_id()}", f"-1 * {lhs}", "*", lhs_rhs, NEG_1)
                lhs_rhs = lhs.lhs
                operator = "+"
                with monkeys.mutate() as mm:
                    mm.set(NEG_1.name, NEG_1)
                    mm.set(lhs_lhs.name, lhs_lhs)
                    mm.set(lhs.name, lhs)
                    monkeys = mm.finish()
            elif operator == "/":
                operator = "*"
                lhs_rhs = rhs
                rhs = lhs_lhs

        rhs = OperatorMonkey(
            f"numbr-{gen_id()}", INVERTED_OPERATOR[operator], rhs.name, lhs_rhs.name
        ).value(monkeys)
        lhs = lhs_lhs
        return Human(f"humn-{gen_id()}", str(lhs), "==", lhs, rhs).unwind(
            monkeys.set(rhs.name, rhs)
        )


def part1(text: str) -> int | None:
    monkey_list = [Monkey.parse(line) for line in text.splitlines()]
    monkeys = immutables.Map({m.name: m for m in monkey_list})
    result = monkeys["root"].value(monkeys)
    assert isinstance(result, NumberMonkey)
    return result.number


def part2(text: str) -> int | None:
    monkey_list = [Monkey.parse(line, True) for line in text.splitlines()]
    monkeys = immutables.Map({m.name: m for m in monkey_list})
    formula = monkeys["root"].value(monkeys)
    assert isinstance(formula, Human)
    return formula.unwind(monkeys)
