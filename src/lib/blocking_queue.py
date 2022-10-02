from lib.constants import TIMEOUT


class BlockingQueue:
    def __init__(self, queue):
        self.queue = queue

    def receive(self):
        return self.queue.get(True, TIMEOUT)
