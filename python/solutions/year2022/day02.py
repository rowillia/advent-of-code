SCORES = {-1: 0, 0: 3, 1: 6, 2: 0, -2: 6}
VALUES = {"A": 1, "X": 1, "B": 2, "Y": 2, "C": 3, "Z": 3}
THROW_ORDER = "ABC"


def score_round(line: str) -> int:
    p1, p2 = line.strip().split(" ")
    return VALUES[p2] + SCORES[VALUES[p2] - VALUES[p1]]


def choose_throw(line: str) -> str:
    p1, p2 = line.strip().split(" ")

    if p2 == "Z":
        return f"{p1} {THROW_ORDER[VALUES[p1] % 3]}"
    if p2 == "Y":
        return f"{p1} {p1}"
    if p2 == "X":
        return f"{p1} {THROW_ORDER[(VALUES[p1] - 2) % 3]}"
    raise Exception(f"Invalid second throw: {p2}")


def part1(text: str) -> int | None:
    return sum(score_round(x) for x in text.splitlines())


def part2(text: str) -> int | None:
    return sum(score_round(choose_throw(x)) for x in text.splitlines())
