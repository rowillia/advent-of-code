from dataclasses import dataclass, field
from functools import cached_property
from typing import Callable, Dict, Iterator, Optional, Tuple


TOTAL_DISK_SIZE = 70000000
REQUIRED_FREE_SPACE = 30000000


@dataclass
class Directory:
    name: str
    parent: Optional["Directory"] = None
    subdirectories: Dict[str, "Directory"] = field(default_factory=dict)
    files: Dict[str, int] = field(default_factory=dict)

    def cd(self, child: str) -> "Directory":
        return self.subdirectories.setdefault(child, Directory(child, self))

    @cached_property
    def total_size(self) -> int:
        return sum(self.files.values()) + sum(
            x.total_size for x in self.subdirectories.values()
        )

    def visit(self, callback: Callable[["Directory"], None]) -> None:
        callback(self)
        for subdir in self.subdirectories.values():
            subdir.visit(callback)


def parse_line(line: str, current_directory: Directory) -> None:
    match line.split():
        case ["dir", name]:
            current_directory.cd(name)
        case [file_size, name]:
            current_directory.files[name] = int(file_size)


def parse_command(
    command: str, input: Iterator[str], current_directory: Directory
) -> Tuple[str | None, Directory]:
    next_line: str | None
    command = command.lstrip(" $")
    match command.split():
        case ["ls"]:
            while next_line := next(input, None):
                if next_line.startswith("$"):
                    break
                parse_line(next_line, current_directory)
            return next_line, current_directory
        case ["cd", dir_name]:
            next_command = next(input, None)
            if dir_name == "..":
                if current_directory.parent is None:
                    raise Exception("No parent directory")
                return next_command, current_directory.parent
            return next_command, current_directory.cd(dir_name)
    return None, current_directory


def parse_input(text: str) -> Directory:
    root = Directory("")
    lines = iter(text.splitlines())
    next_command: str | None = next(lines)

    cwd = root
    while next_command is not None:
        next_command, cwd = parse_command(next_command, lines, cwd)

    return root


def part1(text: str) -> int | None:
    root = parse_input(text)
    total_size = 0

    def func(dir: Directory) -> None:
        nonlocal total_size
        if dir.total_size < 100000:
            total_size += dir.total_size

    root.visit(func)

    return total_size


def part2(text: str) -> int | None:
    root = parse_input(text)
    to_free = root.total_size - (TOTAL_DISK_SIZE - REQUIRED_FREE_SPACE)
    min_size = root.total_size

    def func(dir: Directory) -> None:
        nonlocal min_size
        if dir.total_size >= to_free and dir.total_size < min_size:
            min_size = dir.total_size

    root.visit(func)

    return min_size
