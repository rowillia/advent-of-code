DIGIT_STRINGS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
}


def to_digits(text: str) -> list[list[int]]:
    return [[int(c) for c in line if c.isnumeric()] for line in text.splitlines()]


def text_to_digit(text: str) -> str:
    for digit_str, number in DIGIT_STRINGS.items():
        text = text.replace(digit_str, digit_str[0] + str(number) + digit_str)
    return text


def part1(text: str) -> str | None:
    return sum(10 * x[0] + x[-1] for x in to_digits(text))


def part2(text: str) -> str | None:
    return part1(text_to_digit(text))
