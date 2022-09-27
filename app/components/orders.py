import queue
import functools

global order_queue
global ordered_food_queue

order_queue = []
ordered_food_queue = queue.PriorityQueue()

@functools.total_ordering
class Prioritize:

    def __init__(self, priority, ready_item):
        self.priority = priority
        self.ready_item = ready_item

    def __eq__(self, other):
        return self.priority == other.priority

    def __lt__(self, other):
        return self.priority < other.priority