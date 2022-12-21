from dataclasses import dataclass
from enum import Enum, auto
from functools import cache, cached_property
import math
import re
from typing import Iterable, Set, Tuple

import immutables


ROBOT_RE = re.compile(r"Each (\w+) robot costs ([\w\d\s]+).?")


class Resource(Enum):
    ORE = auto()
    CLAY = auto()
    OBSIDIAN = auto()
    GEODE = auto()


@cache
def join_maps(
    a: immutables.Map[Resource, int], b: immutables.Map[Resource, int]
) -> immutables.Map[Resource, int]:
    result = a.mutate()
    for r, v in b.items():
        result[r] = result.get(r, 0) + v
    return result.finish()


@cache
def diff_maps(
    a: immutables.Map[Resource, int], b: immutables.Map[Resource, int]
) -> immutables.Map[Resource, int]:
    result = a.mutate()
    for r, v in b.items():
        result[r] = result.get(r, 0) - v
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
    ) -> Set[Tuple[immutables.Map[Resource, int], immutables.Map[Resource, int]]]:
        result: Set[
            Tuple[immutables.Map[Resource, int], immutables.Map[Resource, int]]
        ] = set([(immutables.Map(), resources)])
        for resource_type in reversed(Resource):
            spent = resources.mutate()
            valid = True
            robot = self.robots[resource_type]
            for resource, cost in robot.cost.items():
                spent[resource] = spent.get(resource, 0) - cost
                if spent[resource] < 0:
                    valid = False
                    break
            if valid:
                remaining = spent.finish()
                children = self.spend_resources(remaining)
                for child in children:
                    result.add(
                        (
                            child[0].set(
                                robot.robot_type, child[0].get(robot.robot_type, 0) + 1
                            ),
                            child[1],
                        )
                    )
        return result


@dataclass(frozen=True)
class State:
    time_remaining: int
    resources: immutables.Map[Resource, int]
    robots: immutables.Map[Resource, int]
    blueprint: Blueprint

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

    @cache
    def time_to_build(self, resource: Resource) -> float:
        robot_cost = self.blueprint.robots[resource]
        resources = self.resources
        for time in range(self.time_remaining):
            diff = diff_maps(resources, robot_cost.cost)
            if all(x > 0 for x in diff.values()):
                return time
            resources = join_maps(resources, self.robots)
        return math.inf

    def progress(self) -> Iterable["State"]:
        last = Resource.GEODE
        target = Resource.GEODE
        for resource in reversed(Resource):
            if resource in self.robots:
                target = last
                break
            last = resource

        spend_nothing = State(
            self.time_remaining - 1,
            join_maps(self.robots, self.resources),
            self.robots,
            self.blueprint,
        )

        if self.time_remaining > 0:
            children = self.blueprint.spend_resources(self.resources)
            has_target = []
            candidates = []
            for new_robots, remaining_resources in children:
                new_state = State(
                    self.time_remaining - 1,
                    join_maps(self.robots, remaining_resources),
                    join_maps(new_robots, self.robots),
                    self.blueprint,
                )
                if target in new_robots:
                    has_target.append(new_state)
                else:
                    candidates.append(new_state)
            if has_target:
                if self.time_remaining == 1:
                    yield has_target[0]
                else:
                    yield from has_target
            else:
                time_to_build = list(
                    sorted(
                        [(x.time_to_build(target), x) for x in candidates],
                        key=lambda x: x[0],
                    )
                )
                min_time_to_build = time_to_build[0][0]
                if min_time_to_build == math.inf:
                    yield spend_nothing
                else:
                    yield from (
                        y[1] for y in time_to_build if y[0] == min_time_to_build
                    )


def blueprint_quality(blueprint: Blueprint) -> int:
    closed: Set[State] = set()
    open: Set[State] = {
        State(24, immutables.Map(), immutables.Map([(Resource.ORE, 1)]), blueprint)
    }
    finished: Set[Tuple[int, int, int]] = set()
    max_obsidian = 0
    while open:
        next_state = open.pop()
        for child in next_state.progress():
            if (
                Resource.GEODE in child.robots
                and child.time_to_build(Resource.GEODE) == math.inf
            ):
                key = (
                    child.resources.get(Resource.GEODE, 0),
                    child.robots[Resource.GEODE],
                    child.time_remaining,
                )
                if key in finished:
                    continue
                finished.add(key)
            if child not in closed and child not in open:
                open.add(child)
        if next_state.time_remaining == 0:
            if next_state.resources.get(Resource.GEODE, 0) > max_obsidian:
                max_obsidian = next_state.resources[Resource.GEODE]
        closed.add(next_state)
    return max_obsidian


def part1(text: str) -> int | None:
    blueprints = [Blueprint.parse(line) for line in text.splitlines()]
    return max(blueprint_quality(b) for b in blueprints)


def part2(text: str) -> str | None:
    return None
