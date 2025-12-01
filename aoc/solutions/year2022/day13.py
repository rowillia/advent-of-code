from functools import cmp_to_key
from itertools import zip_longest
import json
from typing import Any


def cmp(lhs: Any, rhs: Any) -> int:
    if isinstance(lhs, int) and isinstance(rhs, int):
        return max(-1, min(1, lhs - rhs))
    elif isinstance(lhs, list) and isinstance(rhs, list):
        for l_val, r_val in zip_longest(lhs, rhs, fillvalue=None):
            if l_val is None:
                return -1
            elif r_val is None:
                return 1
            child_result = cmp(l_val, r_val)
            if child_result != 0:
                return child_result
        return 0
    else:
        if isinstance(lhs, int):
            lhs = [lhs]
        else:
            rhs = [rhs]
        return cmp(lhs, rhs)


def part1(text: str) -> int | None:
    pairs = text.split("\n\n")
    result = 0
    for idx, pair in enumerate(pairs):
        lhs, rhs = pair.splitlines()
        if cmp(json.loads(lhs), json.loads(rhs)) == -1:
            result += idx + 1
    return result


def part2(text: str) -> int | None:
    values = [json.loads(line) for line in text.splitlines() if line]
    divider_packets = [[[6]], [[2]]]
    sorted_input = sorted(values + divider_packets, key=cmp_to_key(cmp))
    return (sorted_input.index(divider_packets[0]) + 1) * (
        sorted_input.index(divider_packets[1]) + 1
    )
