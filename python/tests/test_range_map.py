from typing import List, Tuple
from python.common.range_map import add_range


def test_range_map() -> None:
    test: List[Tuple[float, float]] = []
    add_range(test, (3, 8))
    assert test == [(3, 8)]
    add_range(test, (4, 6))
    assert test == [(3, 8)]
    add_range(test, (5, 10))
    assert test == [(3, 10)]
    add_range(test, (0, 12))
    assert test == [(0, 12)]
    add_range(test, (20, 22))
    assert test == [(0, 12), (20, 22)]
    add_range(test, (20, 22))
    assert test == [(0, 12), (20, 22)]
    add_range(test, (18, 21))
    assert test == [(0, 12), (18, 22)]
    add_range(test, (15, 30))
    assert test == [(0, 12), (15, 30)]
    add_range(test, (10, 20))
    assert test == [(0, 30)]
    add_range(test, (35, 40))
    assert test == [(0, 30), (35, 40)]
    add_range(test, (45, 50))
    assert test == [(0, 30), (35, 40), (45, 50)]
    add_range(test, (60, 100))
    assert test == [(0, 30), (35, 40), (45, 50), (60, 100)]
    add_range(test, (5, 55))
    assert test == [(0, 55), (60, 100)]
    add_range(test, (-1, 110))
    assert test == [(-1, 110)]
