from dataclasses import dataclass
from functools import cached_property
from typing import Callable, Dict, Generic, Iterable, List, Protocol, Tuple, TypeVar

from immutables import Map

from python.common.priority_queue import PriorityQueue

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class Optimizable(Protocol[T_co]):
    @cached_property
    def is_finished(self) -> bool: ...

    @cached_property
    def heuristic(self) -> int: ...

    def egress(self) -> Iterable[Tuple["Optimizable[T_co]", int]]: ...


@dataclass(frozen=True)
class OptimizeWrapper(Generic[T]):
    current: T
    end: T
    _heuristic: Callable[[T, T], int]
    _egress: Callable[[T], Iterable[Tuple[T, int]]]

    @property
    def is_finished(self) -> bool:
        return self.current == self.end

    @property
    def heuristic(self) -> int:
        return self._heuristic(self.current, self.end)

    def egress(self) -> Iterable[Tuple["OptimizeWrapper[T]", int]]:
        for neighbor, weight in self._egress(self.current):
            yield (
                OptimizeWrapper(neighbor, self.end, self._heuristic, self._egress),
                weight,
            )


def astar_with_cost(
    start: T,
    end: T,
    heuristic: Callable[[T, T], int],
    neighbors: Callable[[T], Iterable[Tuple[T, int]]],
) -> tuple[List[T], int]:
    wrapped: OptimizeWrapper[T] = OptimizeWrapper(start, end, heuristic, neighbors)
    result, cost = astar_optimizable(wrapped)  # type: ignore
    return [x.current for x in result], cost


def astar(
    start: T,
    end: T,
    heuristic: Callable[[T, T], int],
    neighbors: Callable[[T], Iterable[Tuple[T, int]]],
) -> List[T]:
    return astar_with_cost(start, end, heuristic, neighbors)[0]


def astar_optimizable(start: Optimizable[T]) -> tuple[List[T], int]:
    open_list: PriorityQueue[Optimizable[T]] = PriorityQueue()
    path: Dict[Optimizable[T], Tuple[Optimizable[T], int]] = {}
    open_list.push(start, 0)
    while open_list:
        node = open_list.pop()
        node_cost = 0
        if node in path:
            node_cost = path[node][1]
        if node.is_finished:
            result: List[Optimizable[T]] = [node]
            while node != start:
                node = path[node][0]
                result.append(node)
            return list(reversed(result)), node_cost  # type: ignore
        for neighbor, weight in node.egress():
            g_cost = node_cost + weight
            existing_neighbor = path.get(neighbor, None)
            if existing_neighbor is None or (g_cost < existing_neighbor[1]):
                path[neighbor] = (node, g_cost)
                open_list.push(neighbor, g_cost + node.heuristic)
    raise Exception("No path found")


def djikstra(
    start: T,
    end: T,
    neighbors: Callable[[T], Iterable[Tuple[T, int]]],
) -> Map[T, int]:
    open_list: PriorityQueue[T] = PriorityQueue()
    result: dict[T, int] = {}
    open_list.push(start, 0)
    while open_list:
        node, cost = open_list.pop_with_priorty()
        result[node] = cost
        for neighbor, neighbor_cost in neighbors(node):
            if neighbor not in result:
                open_list.push(neighbor, cost + neighbor_cost)
    return Map(result)
