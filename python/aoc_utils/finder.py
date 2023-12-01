from dataclasses import dataclass
from importlib import util
from pathlib import Path
from types import ModuleType
from typing import List

from yaml import safe_load


@dataclass
class Day:
    year: int
    day_number: int
    module: ModuleType
    solution_input: str | None
    example_input: str
    example_answers: List[str]

    def __str__(self) -> str:
        return f"Day {self.day_number} ({self.year})"


def get_days(years: List[int] | None = None) -> List[Day]:
    days: List[Day] = []
    project_path = Path(__file__).resolve().parent.parent
    if years is None:
        years = [
            int(d.name) for d in (project_path / "solutions").iterdir() if d.is_dir()
        ]

    for year in years:
        solutions_path = project_path / "solutions" / str(year)
        if not solutions_path.exists():
            return []

        examples_path = project_path.parent / "examples" / str(year)
        inputs = project_path.parent / "inputs" / str(year)

        for py_file in solutions_path.glob("*.py"):
            day_number = py_file.name[-5:-3]
            if not day_number.isnumeric():
                continue
            spec = util.spec_from_file_location("", py_file)
            if not spec:
                raise Exception(f"Unable to load module {py_file}")
            module = util.module_from_spec(spec)
            if not spec.loader:
                raise Exception(f"Unable to load module {py_file}")
            spec.loader.exec_module(module)

            example_yaml = safe_load((examples_path / f"{day_number}.yaml").read_text())

            solution_input = None
            solution_path = inputs / f"{day_number}.txt"
            if solution_path.exists():
                solution_input = solution_path.read_text()

            days.append(
                Day(
                    year,
                    int(day_number),
                    module,
                    solution_input,
                    str(example_yaml["input"]),
                    [str(x) for x in example_yaml["answers"]],
                )
            )
    return sorted(days, key=lambda x: (x.year, x.day_number))
