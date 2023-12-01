from typing import List


DECRYPTION_KEY = 811589153


def scramble(file: List[int], mix_count: int = 1) -> List[int]:
    count = len(file)
    locations = list(range(count))
    result = file.copy()
    for _ in range(mix_count):
        for idx in range(count):
            val = file[idx]
            location = locations.index(idx)
            new_locaition = (location + val) % (count - 1)
            if new_locaition == 0:
                new_locaition = count - 1
            result.pop(location)
            locations.pop(location)
            result.insert(new_locaition, val)
            locations.insert(new_locaition, idx)
    return result


def part1(text: str) -> int | None:
    result = scramble([int(x) for x in text.splitlines()])
    zero_index = result.index(0)
    return sum(result[((x * 1000) + zero_index) % len(result)] for x in range(1, 4))


def part2(text: str) -> int | None:
    result = scramble([int(x) * DECRYPTION_KEY for x in text.splitlines()], 10)
    zero_index = result.index(0)
    return sum(result[((x * 1000) + zero_index) % len(result)] for x in range(1, 4))
