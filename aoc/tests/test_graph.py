from typing import Iterable, Tuple

from immutables import Map

from aoc.common.graph import astar, djikstra


def test_astar() -> None:
    def heuristic(a: str, b: str) -> int:
        return abs(ord(a) - ord(b))

    def neighbors(a: str) -> Iterable[Tuple[str, int]]:
        if a == "c":
            return [("d", 1), ("p", 1)]
        elif a == "s":
            return [("t", 1), ("z", 3)]
        elif ord(a) < ord("z"):
            return [(chr(ord(a) + 1), 1)]
        return []

    assert astar("a", "z", heuristic, neighbors) == [
        "a",
        "b",
        "c",
        "p",
        "q",
        "r",
        "s",
        "z",
    ]


def test_djikstra() -> None:
    def neighbors(a: str) -> Iterable[Tuple[str, int]]:
        if a == "c":
            return [("d", 1), ("f", 1)]
        elif a == "b":
            return [("f", 10), ("c", 1)]
        elif ord(a) < ord("f"):
            return [(chr(ord(a) + 1), 1)]
        return []

    assert djikstra("a", neighbors) == Map(
        {
            "a": 0,
            "b": 1,
            "c": 2,
            "d": 3,
            "e": 4,
            "f": 3,
        }
    )
