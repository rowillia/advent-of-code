from typing import TypeVar, Iterable

from itertools import islice


T = TypeVar("T")


def chunks(items: Iterable[T], chunk_size: int) -> Iterable[Iterable[T]]:
    iterator = iter(items)
    while chunk := list(islice(iterator, chunk_size)):
        yield chunk


def priority(badge: str) -> int:
    return (ord(badge.lower()) - ord("a") + 1) + (int(badge.isupper()) * 26)


def score_rucksack(line: str) -> int:
    compartment1, compartment2 = set(line[: len(line) // 2]), set(
        line[len(line) // 2 :]
    )
    return priority(compartment1.intersection(compartment2).pop())


def find_badge_priority(rucksacks: Iterable[str]) -> int:
    return priority(set.intersection(*[set(x) for x in rucksacks]).pop())


def part1(text: str) -> int | None:
    return sum(score_rucksack(x) for x in text.splitlines())


def part2(text: str) -> int | None:
    return sum(find_badge_priority(x) for x in chunks(text.splitlines(), 3))
