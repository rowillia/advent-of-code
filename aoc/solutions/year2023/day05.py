from dataclasses import dataclass
import re


@dataclass
class Range:
    source: int
    dest: int
    range: int

    @classmethod
    def parse(cls, text: str) -> "Range":
        source, dest, range = text.split()
        return cls(int(dest), int(source), int(range))

    def map(self, value: int) -> int:
        if value in self:
            return self.dest + (value - self.source)
        return value

    def map_range(
        self, value: tuple[int, int]
    ) -> tuple[tuple[int, int], list[tuple[int, int]]]:
        start, range = value
        unmapped = []

        if start < self.source:
            unmapped.append((start, self.source - start))
        remapped = (
            self.dest + max(0, start - self.source),
            min(range, min(self.range, (self.source + self.range) - start)),
        )
        if start + range > self.source + self.range:
            unmapped.append(
                (self.source + self.range, start + range - (self.source + self.range))
            )
        return remapped, unmapped

    def __contains__(self, value: int | tuple[int, int]) -> bool:
        if isinstance(value, int):
            return self.source <= value < self.source + self.range
        else:
            return (value[0] <= self.source < value[0] + value[1]) or (
                self.source <= value[0] < self.source + self.range
            )

    def __lt__(self, other: "Range") -> bool:
        return self.source < other.source


@dataclass
class ResourceMap:
    source: str
    dest: str
    ranges: list[Range]

    @classmethod
    def parse(cls, text: list[str]) -> "ResourceMap":
        first_line = text[0]
        if match := re.match(r"([a-z]*)-to-([a-z]*) map:", first_line):
            source, dest = match.groups()
            ranges = []
            for next_line in text[1:]:
                ranges.append(Range.parse(next_line))
            return ResourceMap(source, dest, sorted(ranges))
        else:
            raise Exception(f"Invalid map: {first_line}")

    def map(self, value: int) -> int:
        for r in self.ranges:
            if value in r:
                return r.map(value)
        return value

    def map_range(self, value: tuple[int, int]) -> list[tuple[int, int]]:
        result = []
        values = [value]
        for r in self.ranges:
            next_values = []
            remapped = None
            for value in values:
                if value in r:
                    remapped, unmapped = r.map_range(value)
                    result.append(remapped)
                    next_values.extend(unmapped)
            if remapped:
                values = next_values
        if not result:
            return [value]
        return result + values


@dataclass
class Almanac:
    seeds: list[int]
    resource_maps: dict[str, ResourceMap]

    @classmethod
    def parse(cls, text: str) -> "Almanac":
        parts = text.split("\n\n")
        seeds = [int(x) for x in parts[0].split(":")[1].strip().split()]

        resource_maps = {}
        for resource_map in parts[1:]:
            next_resource = ResourceMap.parse(resource_map.splitlines())
            resource_maps[next_resource.source] = next_resource
        return cls(seeds, resource_maps)

    def map(self) -> list[int]:
        result = []
        for seed in self.seeds:
            current_resource = "seed"
            value = seed
            while current_resource in self.resource_maps:
                next_resource = self.resource_maps[current_resource]
                value = next_resource.map(value)
                current_resource = next_resource.dest
            result.append(value)
        return result

    def map_range(self) -> list[tuple[int, int]]:
        result = []
        for i in range(0, len(self.seeds), 2):
            values = [(self.seeds[i], self.seeds[i + 1])]
            current_resource = "seed"
            while current_resource in self.resource_maps:
                next_resource = self.resource_maps[current_resource]
                next_values = []
                for value in values:
                    mapped_resource = next_resource.map_range(value)
                    next_values.extend(mapped_resource)
                values = next_values
                current_resource = next_resource.dest
            result.extend(values)
        return result


def part1(text: str) -> int | None:
    return min(Almanac.parse(text).map())


def part2(text: str) -> int | None:
    return min(Almanac.parse(text).map_range())[0]
