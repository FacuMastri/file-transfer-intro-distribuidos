class BlockingQueue:
    TIMEOUT = 2
    def __init__(self, queue):
        self.queue = queue

    def receive(self):
        return self.queue.get(True, self.TIMEOUT)

