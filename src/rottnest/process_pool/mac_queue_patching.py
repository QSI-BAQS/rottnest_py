'''
    At-import patching of multiprocessing queue to work fully on mac

    NOTE: Patching is skipped on non-Mac devices
'''

import os

if os.uname().sysname == "Darwin":
    import multiprocessing as mp

    from types import MethodType


    class QsizeCounter():
        def __init__(self):
            self.val = mp.Value('i', 0)

        def put(self):
            with self.val.get_lock():
                self.val.value += 1

        def get(self):
            with self.val.get_lock():
                self.val.value -= 1

        def qsize(self):
            return self.val.value

    # Instantiating a queue forces global start function
    # (otherwise, path mp.queues.Queue does not exist)
    mp.Queue()

    # Patch a qsize counter into mp Queue
    qtype = mp.queues.Queue

    QSIZE_COUNTER_ATTR = "rottnest_qsize_counter"

    def wrap_get(self, block=True, timeout=None):
        counter = getattr(self, QSIZE_COUNTER_ATTR, None)
        if counter is None:
            counter = QsizeCounter()
            setattr(self, QSIZE_COUNTER_ATTR, counter)
        counter.get()
        return self.internal_get(block=block, timeout=timeout)

    def wrap_put(self, obj, block=True, timeout=None):
        counter = getattr(self, QSIZE_COUNTER_ATTR, None)
        if counter is None:
            counter = QsizeCounter()
            setattr(self, QSIZE_COUNTER_ATTR, None)
        counter.put()
        return self.internal_put(obj, block=block, timeout=timeout)

    def patched_qsize(self):
        counter = getattr(self, QSIZE_COUNTER_ATTR, None)
        if counter is None:
            counter = QsizeCounter()
            setattr(self, QSIZE_COUNTER_ATTR, None)
        return counter.qsize()


    qtype.internal_get = qtype.get
    qtype.get = wrap_get
    qtype.internal_put = qtype.put
    qtype.put = wrap_put
    qtype.qsize = patched_qsize

