from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, Set, Tuple


@dataclass(frozen=True)
class Point3D:
    x: int
    y: int
    z: int

    @classmethod
    def parse(cls, text: str) -> Set["Point3D"]:
        points = set()
        for line in text.splitlines():
            x, y, z = line.split(",")
            points.add(Point3D(int(x), int(y), int(z)))
        return points


def count_sides(points: Iterable[Point3D]) -> int:
    xy: Dict[Tuple[int, int], Set[int]] = defaultdict(set)
    xz: Dict[Tuple[int, int], Set[int]] = defaultdict(set)
    yz: Dict[Tuple[int, int], Set[int]] = defaultdict(set)

    result = 0
    for point in points:
        xy[(point.x, point.y)].add(point.z)
        xz[(point.x, point.z)].add(point.y)
        yz[(point.y, point.z)].add(point.x)

    result = 0
    for point in points:
        if point.x - 1 not in yz[(point.y, point.z)]:
            result += 1
        if point.x + 1 not in yz[(point.y, point.z)]:
            result += 1
        if point.y - 1 not in xz[(point.x, point.z)]:
            result += 1
        if point.y + 1 not in xz[(point.x, point.z)]:
            result += 1
        if point.z - 1 not in xy[(point.x, point.y)]:
            result += 1
        if point.z + 1 not in xy[(point.x, point.y)]:
            result += 1

    return result


def flood_fill_water(points: Set[Point3D]) -> int:
    min_corner = Point3D(
        min(p.x for p in points) - 1,
        min(p.y for p in points) - 1,
        min(p.z for p in points) - 1,
    )
    max_corner = Point3D(
        max(p.x for p in points) + 1,
        max(p.y for p in points) + 1,
        max(p.z for p in points) + 1,
    )
    result = 0
    remaining = {min_corner}
    visited: Set[Point3D] = set()
    while remaining:
        next_cell = remaining.pop()
        if next_cell in visited:
            continue
        neighbors = [
            Point3D(next_cell.x + 1, next_cell.y, next_cell.z),
            Point3D(next_cell.x - 1, next_cell.y, next_cell.z),
            Point3D(next_cell.x, next_cell.y + 1, next_cell.z),
            Point3D(next_cell.x, next_cell.y - 1, next_cell.z),
            Point3D(next_cell.x, next_cell.y, next_cell.z + 1),
            Point3D(next_cell.x, next_cell.y, next_cell.z - 1),
        ]
        for neighbor in neighbors:
            if neighbor in points:
                result += 1
            elif (
                (min_corner.x <= neighbor.x <= max_corner.x)
                and (min_corner.y <= neighbor.y <= max_corner.y)
                and (min_corner.z <= neighbor.z <= max_corner.z)
                and neighbor not in visited
                and neighbor not in remaining
            ):
                remaining.add(neighbor)
        visited.add(next_cell)

    return result


def part1(text: str) -> int | None:
    return count_sides(Point3D.parse(text))


def part2(text: str) -> int | None:
    return flood_fill_water(Point3D.parse(text))
