from collections import defaultdict
from dataclasses import dataclass
import re


CARD_RE = re.compile(r"Card\s+(\d+):\s+([\d\s]+)\|\s+([\d\s]+)")


@dataclass
class Card:
    number: int
    winning_numbers: set[int]
    card_numbers: set[int]

    @property
    def matches(self) -> int:
        return len(self.card_numbers & self.winning_numbers)

    @property
    def score(self) -> int:
        matches = self.matches
        return 1 << (matches - 1) if matches > 0 else 0

    @classmethod
    def parse(cls, text: str) -> "Card":
        if match := CARD_RE.match(text.strip()):
            num_str, winning_str, card_str = match.groups()
            return cls(
                int(num_str),
                {int(num) for num in winning_str.strip().split()},
                {int(num) for num in card_str.strip().split()},
            )
        else:
            raise ValueError(f"Invalid card: {text}")


def part1(text: str) -> int | None:
    cards = [Card.parse(card).score for card in text.splitlines()]
    return sum(Card.parse(card).score for card in text.splitlines())


def part2(text: str) -> int | None:
    cards = [Card.parse(card) for card in text.splitlines()]
    counts: dict[int, int] = {card.number: 1 for card in cards}
    for card in cards:
        matches = card.matches
        for next_card in range(card.number + 1, card.number + 1 + matches):
            counts[next_card] += counts[card.number]
    return sum(counts.values())
