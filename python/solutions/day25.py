import math


DECODER = {"=": -2, "-": -1, "0": 0, "1": 1, "2": 2}
ENCODER = {v: k for k, v in DECODER.items()}


def snafu_to_dec(text: str) -> int:
    result = 0
    for power, value in enumerate(reversed(text)):
        result += DECODER[value] * (5**power)
    return result


def dec_to_snafu(value: int) -> str:
    result = []
    remainder = value
    power = math.ceil(math.log(abs(value), 5))
    ub = snafu_to_dec("2" * (power))
    while power >= 0:
        for key, value in DECODER.items():
            value_at_digit = (value) * (5**power)
            if (value_at_digit - ub) <= remainder <= (value_at_digit + ub):
                result.append(key)
                remainder -= value_at_digit
                break
        power -= 1
        ub -= 2 * (5**power)
    return "".join(result).lstrip("0")


def part1(text: str) -> str | None:
    return dec_to_snafu(sum(snafu_to_dec(x) for x in text.splitlines()))


def part2(text: str) -> str | None:
    return None
