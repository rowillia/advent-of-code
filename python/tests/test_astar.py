from typing import List, Tuple
from common.astar import astar


def test_astar() -> None:
    def heuristic(a: str, b: str) -> int:
        return abs(ord(a) - ord(b))

    def neighbors(a: str) -> List[Tuple[str, int]]:
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
