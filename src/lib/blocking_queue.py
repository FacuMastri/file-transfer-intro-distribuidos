class BlockingQueue:
    def __init__(self, queue):
        self.queue = queue
        self.timeout = 2

    def receive(self):
        return self.queue.get(True, self.timeout)

    def settimeout(self, timeout):
        self.timeout = timeout