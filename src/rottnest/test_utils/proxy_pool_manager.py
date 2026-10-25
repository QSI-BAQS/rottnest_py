import queue

class ProxyPoolManager:

    def __init__(self):

        self.priority_task_queue = queue.Queue()
