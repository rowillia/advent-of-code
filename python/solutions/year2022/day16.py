from dataclasses import dataclass
from functools import cache, cached_property
import re
from typing import Dict, Iterator, List, Set, Tuple

import immutables

from python.common.astar import astar
from python.common.priority_queue import PriorityQueue

VALVE_RE = re.compile(
    r"Valve (\w+) has flow rate=(\d+); tunnels? leads? to valves? ([\w\,\s]+)"
)


@dataclass(frozen=True)
class Valve:
    name: str
    flow_rate: int
    egress: Tuple[str, ...]

    @classmethod
    def parse(cls, line: str) -> "Valve":
        if match := VALVE_RE.match(line):
            name, flow_rate, egress = match.groups()
            return Valve(name, int(flow_rate), tuple(egress.split(", ")))
        raise Exception(f"Invalid valve: {line}")


@cache
def distance_map(valves: immutables.Map[str, Valve]) -> Dict[Tuple[str, str], int]:
    result: Dict[Tuple[str, str], int] = {}

    def heuristic(a: str, b: str) -> int:
        if a == b:
            return 0
        if a in valves[b].egress:
            return 1
        return 2

    def neighbors(a: str) -> List[Tuple[str, int]]:
        return [(x, 1) for x in valves[a].egress]

    for origin in valves:
        for dest in valves:
            result[(origin, dest)] = len(astar(origin, dest, heuristic, neighbors))

    return result


@dataclass(frozen=True)
class ValveNode:
    valve: Valve
    opened_at: int | None

    def open(self, time: int) -> "ValveNode":
        return ValveNode(self.valve, time)

    @classmethod
    def wrap(cls, valve: Valve) -> "ValveNode":
        return ValveNode(valve, None)

    @cached_property
    def value(self) -> int:
        if self.opened_at is None:
            return 0
        return (31 - self.opened_at) * self.valve.flow_rate

    @cached_property
    def _hash(self) -> int:
        return hash((self.valve, self.value))

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ValveNode):
            return False
        return self.valve == other.valve and self.value == other.value


@dataclass(frozen=True)
class Volcano:
    valves: immutables.Map[str, ValveNode]
    time: int
    locations: Tuple[str, ...]
    value: int

    @classmethod
    def build(
        cls, valves: List[Valve], worker_count: int = 1, start_time: int = 1
    ) -> "Volcano":
        return Volcano(
            immutables.Map([(x.name, ValveNode.wrap(x)) for x in valves]),
            start_time,
            ("AA",) * worker_count,
            0,
        )

    def supercedes(self, other: "Volcano") -> bool:
        return (
            self.valves == other.valves
            and sorted(self.locations) == sorted(other.locations)
            and self.potential > other.potential
        )

    def egress(self, time: int, idx: int = 0) -> Iterator["Volcano"]:
        current_node = self.valves[self.locations[idx]]
        children: Set[Volcano] = set()
        last_child = idx == (len(self.locations) - 1)
        if current_node.opened_at is None and current_node.valve.flow_rate > 0:
            opened_node = current_node.open(time)
            child_with_open_valve = Volcano(
                self.valves.set(
                    current_node.valve.name,
                    opened_node,
                ),
                time,
                self.locations,
                self.value + opened_node.value,
            )
            children.add(child_with_open_valve)
        for outflow in current_node.valve.egress:
            child_locations = list(self.locations)
            child_locations[idx] = outflow
            children.add(Volcano(self.valves, time, tuple(child_locations), self.value))
        if not last_child:
            new_children: Dict[Tuple[str, ...], Volcano] = {}
            for child in children:
                for sub_child in child.egress(time, idx + 1):
                    new_children[tuple(sorted(sub_child.locations))] = sub_child
            children = set(new_children.values())

        yield from children

    @cached_property
    def potential(self) -> int:
        assert distances is not None
        unopened_value = 0
        for valve in self.valves.values():
            valve_defn = valve.valve
            if valve_defn.flow_rate > 0 and valve.opened_at is None:
                shortest_distance = min(
                    distances[(loc, valve_defn.name)] for loc in self.locations
                )
                unopened_value += valve_defn.flow_rate * (
                    30 - (self.time + shortest_distance)
                )
        return self.value + unopened_value

    @cached_property
    def complete(self) -> bool:
        return self.time == 30 or all(
            (x.valve.flow_rate == 0 or x.opened_at is not None)
            for x in self.valves.values()
        )


def solve(volvano: Volcano) -> int:
    open_list: PriorityQueue[Volcano] = PriorityQueue()
    open_list.push(volvano, volvano.potential)
    best_paths: Dict[
        Tuple[immutables.Map[str, ValveNode], Tuple[str, ...]], Volcano
    ] = {}
    culled = 0
    explored = 0
    while open_list:
        next_node = open_list.pop()
        explored += 1
        if next_node.complete:
            result = next_node.value
            print(f"{culled=} {explored=}")
            return result
        for node in next_node.egress(next_node.time + 1):
            best_key = (node.valves, node.locations)
            if best_key not in best_paths or node.supercedes(best_paths[best_key]):
                open_list.push(node, -1 * node.potential)
                best_paths[best_key] = node
            else:
                culled += 1

    print(f"{culled=}")
    return max(x.value for x in best_paths.values() if x.complete)


distances = None


def part1(text: str) -> int | None:
    v = Volcano.build([Valve.parse(line) for line in text.splitlines()])
    global distances
    distances = distance_map(
        immutables.Map((x.valve.name, x.valve) for x in v.valves.values())
    )
    return solve(v)


def part2(text: str) -> int | None:
    v = Volcano.build([Valve.parse(line) for line in text.splitlines()], 2, 5)
    global distances
    distances = distance_map(
        immutables.Map((x.valve.name, x.valve) for x in v.valves.values())
    )
    return solve(v)
