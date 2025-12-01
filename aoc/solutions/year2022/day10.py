from dataclasses import dataclass
from typing import List


TARGET_CYCLES = list(range(20, 221, 40))


@dataclass
class CPU:
    instructions: List[str]

    def execute(self) -> List[int]:
        register_x = 1
        result: List[int] = [1]
        for instruction in self.instructions:
            result.append(register_x)
            match instruction.split():
                case ["addx", value]:
                    result.append(register_x)
                    register_x += int(value)
        return result

    def render(self) -> List[str]:
        values = self.execute()
        result = [""]
        for x in range(240):
            if abs(len(result[-1]) - values[x + 1]) <= 1:
                result[-1] += "#"
            else:
                result[-1] += "."
            if len(result[-1]) >= 40:
                result.append("")
        return result


def part1(text: str) -> int | None:
    cpu = CPU(text.splitlines())
    values = cpu.execute()
    return sum(values[x] * x for x in TARGET_CYCLES)


def part2(text: str) -> str | None:
    cpu = CPU(text.splitlines())
    return "\n".join(cpu.render())
