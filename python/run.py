from aoc_utils.finder import get_days


def main() -> None:
    days = get_days()
    current_day = days[-1]

    print(f"🎄 Advent of Code: Day {current_day.day_number} 🎄")
    print(
        "\t Part 1: " + getattr(current_day.module, "part1")(current_day.solution_input)
    )
    print(
        "\t Part 2: " + getattr(current_day.module, "part2")(current_day.solution_input)
    )


if __name__ == "__main__":
    main()
