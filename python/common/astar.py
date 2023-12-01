from dataclasses import dataclass
from python.common.priority_queue import PriorityQueue

from typing import Callable, Dict, Generic, Iterable, List, Tuple, TypeVar, Protocol

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class Optimizable(Protocol[T_co]):
    @property
    def is_finished(self) -> bool:
        pass

    @property
    def heuristic(self) -> int:
        pass

    def egress(self) -> Iterable[Tuple["Optimizable[T_co]", int]]:
        pass


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
            yield OptimizeWrapper(
                neighbor, self.end, self._heuristic, self._egress
            ), weight


def astar(
    start: T,
    end: T,
    heuristic: Callable[[T, T], int],
    neighbors: Callable[[T], Iterable[Tuple[T, int]]],
) -> List[T]:
    wrapped: OptimizeWrapper[T] = OptimizeWrapper(start, end, heuristic, neighbors)
    result: List[OptimizeWrapper[T]] = astar_optimizable(wrapped)  # type: ignore
    return [x.current for x in result]


def astar_optimizable(start: Optimizable[T]) -> List[T]:
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
            return list(reversed(result))  # type: ignore
        for neighbor, weight in node.egress():
            g_cost = node_cost + weight
            existing_neighbor = path.get(neighbor, None)
            if existing_neighbor is None or (g_cost < existing_neighbor[1]):
                path[neighbor] = (node, g_cost)
                open_list.push(neighbor, g_cost + node.heuristic)
    raise Exception("No path found")
