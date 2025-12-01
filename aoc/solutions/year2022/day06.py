def find_unique_window(text: str, window_len: int) -> int | None:
    for i in range(len(text)):
        if len(set(text[i : i + window_len])) == window_len:
            return i + window_len
    return None


def part1(text: str) -> int | None:
    return find_unique_window(text, 4)


def part2(text: str) -> int | None:
    return find_unique_window(text, 14)
