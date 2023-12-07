# %%

from collections import Counter
from dataclasses import dataclass
import enum
from functools import cached_property


class CardValue(enum.Enum):
    JOKER = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    def __str__(self) -> str:
        if 2 <= self.value <= 9:
            return str(self.value)
        return str(self.name)[0]

    def __lt__(self, other: "CardValue") -> bool:
        return self.value < other.value

    @classmethod
    def parse(cls, text: str, part2: bool = False) -> "CardValue":
        if text.isdecimal():
            return cls(int(text))
        elif text == "T":
            return cls.TEN
        elif text == "J":
            if part2:
                return cls.JOKER
            return cls.JACK
        elif text == "Q":
            return cls.QUEEN
        elif text == "K":
            return cls.KING
        elif text == "A":
            return cls.ACE
        raise Exception(f"Unknown card value: {text}")


@dataclass(frozen=True)
class Hand:
    cards: tuple[CardValue, ...]

    def __str__(self) -> str:
        return "".join(map(str, self.cards))

    @classmethod
    def parse(cls, text: str, part2: bool = False) -> "Hand":
        return Hand(tuple(map(lambda x: CardValue.parse(x, part2), text)))

    @cached_property
    def value(self) -> int:
        no_jokers = tuple([c for c in self.cards if c != CardValue.JOKER])
        num_jokers = len(self.cards) - len(no_jokers)
        buckets = Counter(no_jokers)
        counts = list(sorted(buckets.values(), reverse=True))
        if num_jokers == 5:
            return 6
        if counts[0] == 5:
            return 6
        if counts[0] == 4:
            return 5 + num_jokers
        if counts[0] == 3 and (len(counts) > 1 and counts[1]) == 2:
            return 4
        if counts[0] == 3:
            return 3 + (num_jokers + 1 if num_jokers else 0)
        if counts[0] == 2 and (len(counts) > 1 and counts[1] == 2):
            return 2 + (num_jokers + 1 if num_jokers else 0)
        if counts[0] == 2:
            if num_jokers == 1:
                return 3
            elif num_jokers >= 2:
                return 3 + num_jokers
            else:
                return 1
        if num_jokers == 1:
            return 1
        elif num_jokers == 2:
            return 3
        elif num_jokers > 2:
            return 2 + num_jokers
        return 0

    def __lt__(self, other: "Hand") -> bool:
        if self.value == other.value:
            return self.cards < other.cards
        return self.value < other.value


def part1(text: str) -> int | None:
    bets = [
        (Hand.parse(h.strip()), int(b.strip()))
        for (h, b) in [line.split() for line in text.splitlines()]
    ]
    result = 0
    for rank, bet in enumerate(sorted(bets), 1):
        result += rank * bet[1]
    return result


def part2(text: str) -> int | None:
    bets = [
        (Hand.parse(h.strip(), part2=True), int(b.strip()))
        for (h, b) in [line.split() for line in text.splitlines()]
    ]
    result = 0
    for rank, bet in enumerate(sorted(bets), 1):
        result += rank * bet[1]
    return result


# %%
