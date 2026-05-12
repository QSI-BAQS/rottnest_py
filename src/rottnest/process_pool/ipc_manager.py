'''
    Inter process communication manager
    Drains pipes and handles asynch communication
'''

# Do on-import patching of Multiprocessing Queue for Mac devices
import rottnest.process_pool.mac_queue_patching

class IPCManager:
    NOT_FOUND = object()

    def __init__(self, pipe):
        self._pipe = pipe
        self._msg_queues = dict()

    def fetch(
            self,
            target: str = None,
            *,
            max_fetch: int = 5,
            blocking: bool = False,
            timeout: int = 20
        ):
        '''
            Fetches up to max_fetch elements from
            a pipe and sorts them based on headers
            Halts early if the pipe is empty unless
            blocking is set to true

            Unlike get_item, this does not attempt to first check
            queues before querying the pipe
        '''
        for fetch in range(max_fetch):

            if not blocking and self._pipe.empty():
                # Check that the pipe is not empty
                break

            header, args = self._pipe.get()
            if header not in self._msg_queues:
                self._msg_queues[header] = list()

            if header == target:
                return args

            self._msg_queues[header].append(args)

        # Target was not found
        return IPCManager.NOT_FOUND

    def __getitem__(self, target):
        '''
            Short hand dispatch
        '''
        return self.get_item(target)

    def flush(self):
        '''
            Flush the pipe
        '''
        while not self._pipe.empty():
            self.get_item(None, blocking=False)
        return

    def clear(self, target):
        '''
            Clears a queue, saving memory
        '''
        lst = self._msg_queues.get(target, None)
        self._msg_queues[target] = list()
        if lst is not None:
            del lst

    def clear_all(self):
        '''
            Clears all message queues
        '''
        self.flush()
        self._msg_queues = dict()

    def batch_get(self, target):
        '''
            Clears a message queue
            # TODO: there seems to be some errors in this function
        '''
        # Initial fetch to populate
        init = self.fetch(target)

        if None is not (queue := 
            self._msg_queues.get(target, None)
        ):
            if len(queue) > 0:
                # Hotswap a new list
                # Any dangling refs should write to the 
                #  old one
                self._msg_queues[target] = list()
                return queue

        return self.NOT_FOUND


    def get_item(
            self,
            target: str,
            *,
            max_fetch: int = 5,
            blocking: bool = False
        ):
        '''
            Gets an item from the IPC manager
        '''
        # Attempts to see if the queue is already
        # Populated with an unprocessed item
        if None is not (queue := self._msg_queues.get(target, None)):
            if len(queue) > 0:
                # Item is enqueued, fetch
                item = queue.pop(0)
                return item
        # Queue not populated, attempt to fetch
        return self.fetch(
            target,
            max_fetch=max_fetch,
            blocking=blocking
        )
