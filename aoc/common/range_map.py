from bisect import bisect
from typing import List, Tuple


def add_range(index: List[Tuple[float, float]], new_range: Tuple[float, float]) -> None:
    insertion_point = bisect(index, new_range)
    left: Tuple[float, float] | None = None

    start_index = insertion_point
    end_index = insertion_point

    if insertion_point > 0:
        left = index[insertion_point - 1]
        if (new_range[0] <= left[1] <= new_range[1]) or (
            left[0] <= new_range[0] <= left[1]
        ):
            # Merge into left
            new_range = (left[0], max(left[1], new_range[1]))
            start_index = insertion_point - 1

    while end_index < len(index) and index[end_index][0] <= new_range[1]:
        # Absorb any positions to the right now covered
        new_range = (new_range[0], max(index[end_index][1], new_range[1]))
        end_index += 1
    index[start_index:end_index] = [new_range]
