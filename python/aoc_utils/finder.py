from dataclasses import dataclass
from importlib import util
from pathlib import Path
from types import ModuleType
from typing import List


@dataclass
class Day:
    day_number: int
    module: ModuleType
    solution_input: str
    example_input: str
    example_answers: List[str]


def get_days() -> List[Day]:
    days: List[Day] = []
    project_path = Path(__file__).resolve().parent.parent
    solutions_path = project_path / "solutions"
    examples_path = project_path / "examples"
    inputs = project_path / "inputs"
    for py_file in solutions_path.glob("*.py"):
        day_number = py_file.name[-5:-3]
        spec = util.spec_from_file_location("", py_file)
        if not spec:
            raise Exception(f"Unable to load module {py_file}")
        module = util.module_from_spec(spec)
        if not spec.loader:
            raise Exception(f"Unable to load module {py_file}")
        spec.loader.exec_module(module)

        example_input = (examples_path / f"{day_number}.txt").read_text()
        example_answers = (
            (examples_path / f"{day_number}_answer.txt").read_text().splitlines()
        )
        solution_input = (inputs / f"{day_number}.txt").read_text()

        days.append(
            Day(int(day_number), module, solution_input, example_input, example_answers)
        )
    return sorted(days, key=lambda x: x.day_number)
