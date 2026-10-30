import queue

class ProxyPoolManager:
    '''
        Proxy of the pool manager for testing
        Mostly this checks receipt of the correct objects
        in queues
    '''

    def __init__(self):
        '''
            Constructor
        '''
        self.priority_task_queue = queue.Queue()

    def submit_priority(self, cmd, *args, **kwargs):
        '''
            Priority queue proxy
        '''
        self.priority_task_queue.put((cmd, args, kwargs))
