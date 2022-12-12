from common.priority_queue import PriorityQueue

from typing import Callable, Dict, List, Tuple, TypeVar

T = TypeVar("T")


def astar(
    start: T,
    end: T,
    heuristic: Callable[[T, T], int],
    neighbors: Callable[[T], List[Tuple[T, int]]],
) -> List[T]:
    open_list: PriorityQueue[T] = PriorityQueue()
    path: Dict[T, Tuple[T, int]] = {}
    open_list.push(start, 0)
    while open_list:
        node = open_list.pop()
        node_cost = 0
        if node in path:
            node_cost = path[node][1]
        if node == end:
            result: List[T] = [node]
            while node != start:
                node = path[node][0]
                result.append(node)
            return list(reversed(result))
        for neighbor, weight in neighbors(node):
            g_cost = node_cost + weight
            if neighbor not in path or (g_cost < path[neighbor][1]):
                path[neighbor] = (node, g_cost)
                open_list.push(neighbor, g_cost + heuristic(neighbor, end))
    raise Exception("No path found")
