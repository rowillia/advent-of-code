from python.common.priority_queue import PriorityQueue


def test_queue() -> None:
    queue: PriorityQueue[str] = PriorityQueue()
    queue.push("hello", 100)
    queue.push("world", 10)
    queue.push("hello", 0)
    assert queue.pop() == "hello"
    assert queue.pop() == "world"
