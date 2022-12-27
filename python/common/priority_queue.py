from dataclasses import dataclass, field
from typing import Dict, List, TypeVar, Generic
from heapq import heappush, heappop


T = TypeVar("T")


@dataclass(order=True)
class PrioritizedItem(Generic[T]):
    priority: int
    item: T = field(compare=False)
    is_removed: bool = field(default=False, compare=False)


@dataclass
class PriorityQueue(Generic[T]):
    _items: List[PrioritizedItem[T]] = field(default_factory=list)
    _entries: Dict[T, PrioritizedItem[T]] = field(default_factory=dict)

    def push(self, item: T, priority: int) -> None:
        if item in self._entries:
            existing_entry = self._entries[item]
            if existing_entry.priority == priority:
                return
            existing_entry.is_removed = True
            item = existing_entry.item
        envelope = PrioritizedItem(priority, item)
        self._entries[item] = envelope
        heappush(self._items, envelope)

    def pop(self) -> T:
        while self._items:
            item = heappop(self._items)
            if not item.is_removed:
                del self._entries[item.item]
                return item.item
        raise Exception("Pop from empty queue")

    def remove(self, item: T) -> None:
        self._entries[item].is_removed = True

    def __contains__(self, item: T) -> bool:
        return item in self._entries and not self._entries[item].is_removed

    def __bool__(self) -> bool:
        return bool(self._entries)
