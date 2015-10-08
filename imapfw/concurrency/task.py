

from collections import deque


class Task(object):
    """Generic task class."""

    def __init__(self):
        self._tasks = deque()

    def append(self, task):
        self._tasks.appendleft(task)

    def getTask(self):
        try:
            return self._tasks.pop()
        except IndexError: # No more task.
            return None
