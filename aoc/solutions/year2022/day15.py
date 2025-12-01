from bisect import bisect
from collections import defaultdict
from dataclasses import dataclass
import re
from typing import Dict, List, Tuple

from aoc.common.point import Point
from aoc.common.range_map import add_range


SENSOR_RE = re.compile(
    r"Sensor at x=(-?\d+), y=(-?\d+): closest beacon is at x=(-?\d+), y=(-?\d+)"
)


@dataclass
class BeaconMap:
    beacons: List[Tuple[Point, Point]]
    exclusion_zones: Dict[int, List[Tuple[float, float]]]

    @classmethod
    def parse(cls, text: str, bounds: Tuple[int, int]) -> "BeaconMap":
        result: List[Tuple[Point, Point]] = []
        exclusion_zones: Dict[int, List[Tuple[float, float]]] = defaultdict(list)
        for line in text.splitlines():
            if match := SENSOR_RE.match(line.strip()):
                sensor_x, sensor_y, beacon_x, beacon_y = (
                    int(x) for x in match.groups()
                )
                sensor = Point(sensor_x, sensor_y)
                beacon = Point(beacon_x, beacon_y)
                distance = sensor.manhattan_distance(beacon)
                for y in range(
                    max(bounds[0], sensor.y - distance),
                    min(bounds[1], sensor.y + distance + 1),
                ):
                    width = distance - abs(sensor.y - y)
                    add_range(
                        exclusion_zones[y],
                        (sensor.x - width, sensor.x + width),
                    )
                result.append((sensor, beacon))
        return BeaconMap(result, exclusion_zones)

    def exclusion_map_for_row(self, row_num: int) -> int:
        range_map: List[Tuple[float, float]] = self.exclusion_zones[row_num]
        return sum([(end - start) for start, end in range_map])  # type: ignore


def part1(text: str) -> int | None:
    input, row_txt = text.split("\n\n")
    row_num = int(row_txt.strip())
    bounds = (row_num, row_num + 1)
    beacon_map = BeaconMap.parse(input, bounds)
    return beacon_map.exclusion_map_for_row(row_num)


def part2(text: str) -> float | None:
    input, row_num = text.split("\n\n")
    bounds = (0, 20) if row_num == "10" else (0, 4_000_000)
    beacon_map = BeaconMap.parse(input, bounds)
    for row, exclusion_zone in beacon_map.exclusion_zones.items():
        idx = bisect(exclusion_zone, bounds) - 1
        if exclusion_zone[idx][0] <= bounds[0] and exclusion_zone[idx][1] >= bounds[1]:
            continue
        return 4_000_000 * (exclusion_zone[idx][1] + 1) + row
    return None
