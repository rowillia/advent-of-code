import bisect
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, auto
from functools import cache, cached_property
import math
import re
from typing import Dict, Iterable, List, Set, Tuple

import immutables

from python.common.priority_queue import PriorityQueue


ROBOT_RE = re.compile(r"Each (\w+) robot costs ([\w\d\s]+).?")


class Resource(Enum):
    ORE = auto()
    CLAY = auto()
    OBSIDIAN = auto()
    GEODE = auto()


def join_maps(
    a: immutables.Map[Resource, int], b: immutables.Map[Resource, int]
) -> immutables.Map[Resource, int]:
    result = a.mutate()
    for r, v in b.items():
        result[r] = a.get(r, 0) + v
    return result.finish()


def diff_maps(
    a: immutables.Map[Resource, int], b: immutables.Map[Resource, int]
) -> immutables.Map[Resource, int] | None:
    result = a.mutate()
    for r, v in b.items():
        item = a.get(r, 0) - v
        if item < 0:
            return None
        result[r] = item
    return result.finish()


@dataclass(frozen=True)
class Robot:
    robot_type: Resource
    cost: immutables.Map[Resource, int]

    @classmethod
    def parse(cls, text: str) -> "Robot":
        text = text.strip()
        if not (match := ROBOT_RE.match(text)):
            raise Exception("Invalid robot: {text}")
        robot_type_str, cost_str = match.groups()
        cost = {}
        for x in cost_str.split(" and "):
            num, resource_type = x.split()
            cost[Resource[resource_type.upper()]] = int(num)
        return Robot(Resource[robot_type_str.upper()], immutables.Map(cost))


@dataclass(frozen=True)
class Blueprint:
    blueprint_id: int
    robots: immutables.Map[Resource, Robot]

    @classmethod
    def parse(cls, text: str) -> "Blueprint":
        text = text.strip()
        blueprint_id_text, recepie = text.split(":")
        return Blueprint(
            int(blueprint_id_text.split()[1]),
            immutables.Map(
                [
                    (r.robot_type, r)
                    for r in (Robot.parse(x) for x in recepie.split(". "))
                ]
            ),
        )

    @cache
    def spend_resources(
        self, resources: immutables.Map[Resource, int]
    ) -> Set[Tuple[Resource | None, immutables.Map[Resource, int]]]:
        result: Set[Tuple[Resource | None, immutables.Map[Resource, int]]] = set(
            [(None, resources)]
        )
        for robot in self.robots.values():
            remaining_resources = diff_maps(resources, robot.cost)

            if remaining_resources is not None:
                result.add((robot.robot_type, remaining_resources))
        return result


@dataclass(frozen=True)
class State:
    time_remaining: int
    resources: immutables.Map[Resource, int]
    robots: immutables.Map[Resource, int]
    blueprint: Blueprint

    def __lt__(self, other: "State") -> bool:
        return (self.resource_count + self.robot_count) < (
            other.resource_count + other.robot_count
        )

    @cached_property
    def resource_count(self) -> int:
        return sum(self.resources.values())

    @cached_property
    def robot_count(self) -> int:
        return sum(self.robots.values())

    @cached_property
    def _hash(self) -> int:
        return hash((self.time_remaining, self.resources, self.robots, self.blueprint))

    def __hash__(self) -> int:
        return self._hash

    @cache
    def existing_total_for_resource(self, resource: Resource) -> int:
        return self.resources.get(resource, 0) + (
            self.robots.get(resource, 0) * self.time_remaining
        )

    @cached_property
    def potential(self) -> Tuple[int, int]:
        resources = self.resources
        robots = self.robots
        for time in range(self.time_remaining):
            old_robots = robots
            for resource in reversed(Resource):
                robot = self.blueprint.robots[resource]
                diff = diff_maps(resources, robot.cost)
                if diff is not None and self.time_remaining - time > 1:
                    robots = robots.set(
                        robot.robot_type, robots.get(robot.robot_type, 0) + 1
                    )
                    if robot.robot_type == Resource.GEODE:
                        resources = diff
                        break
            resources = join_maps(resources, old_robots)
        return resources.get(Resource.GEODE, 0), robots.get(
            Resource.GEODE, 0
        ) - self.robots.get(Resource.GEODE, 0)

    def progress(self) -> Iterable["State"]:
        if self.time_remaining > 0:
            for robot_type, remaining in self.blueprint.spend_resources(self.resources):
                new_robots = self.robots
                if robot_type is not None:
                    new_robots = new_robots.set(
                        robot_type, self.robots.get(robot_type, 0) + 1
                    )
                next_state = State(
                    self.time_remaining - 1,
                    join_maps(remaining, self.robots),
                    new_robots,
                    self.blueprint,
                )
                yield next_state


def blueprint_quality(blueprint: Blueprint, time: int) -> int:
    closed: Set[State] = set()
    open: PriorityQueue[State] = PriorityQueue()
    initial_state = State(
        time, immutables.Map(), immutables.Map([(Resource.ORE, 1)]), blueprint
    )
    open.push(initial_state, -initial_state.potential[0])
    finished = set()
    geode_count = 0
    priority_map: Dict[Tuple[int, int], List[State]] = defaultdict(list)
    while open:
        next_state = open.pop()
        for child in next_state.progress():
            if child not in closed and child not in open:
                potential, new_geod_bots = child.potential
                finished_key = (
                    child.robots.get(Resource.GEODE, 0),
                    child.resources.get(Resource.GEODE, 0),
                    child.time_remaining,
                )
                if new_geod_bots == 0:
                    if finished_key in finished:
                        continue
                    finished.add(finished_key)
                geode_count = max(
                    geode_count, child.existing_total_for_resource(Resource.GEODE)
                )

                if potential >= geode_count:
                    same_priorities = priority_map[(potential, child.time_remaining)]
                    idx = bisect.bisect_left(same_priorities, child)
                    for prior_state in same_priorities[idx:]:
                        if diff_maps(prior_state.robots, child.robots) and diff_maps(
                            prior_state.resources, child.resources
                        ):
                            break
                    else:
                        open.push(child, -potential)
                        bisect.insort(same_priorities, child)
        if next_state.time_remaining == 0:
            return geode_count
        closed.add(next_state)
    return geode_count


def part1(text: str) -> int | None:
    blueprints = [Blueprint.parse(line) for line in text.splitlines()]
    return sum(blueprint_quality(b, 24) * b.blueprint_id for b in blueprints)


def part2(text: str) -> int | None:
    blueprints = [Blueprint.parse(line) for line in text.splitlines()]
    return math.prod(blueprint_quality(b, 32) for b in blueprints[:3])
