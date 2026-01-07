'''
    Thin wrapper on MPI to allow it to work with a queue interface
'''

from mpi4py import MPI

import time

from queue import Empty, Full

TAG_SERVER_NO_PRIO = 1
TAG_CLIENT_NO_PRIO = 2
TAG_SERVER_PRIO = 3
TAG_CLIENT_PRIO = 4

# How much to consume of the remaining timeout if there is one
# (clamped to at least 0.05s)
QUEUE_TIMEOUT_RATE = 0.2

class MPIRootQueue():
    def __init__(self, comm, allocated_clients=None, priority=False):
        '''
            Create the root queue (dispatches jobs)
        '''
        self.comm = comm
        self.rank = comm.Get_rank()
        self.n_peers = comm.Get_size() - 1

        if self.rank != 0:
            raise Exception("Root queue can only be used by MPI root peer")

        # List of all/available clients (identified by rank)
        # TODO : Use a faster data structure (queue?)
        if allocated_clients is None:
            # If there was no allocation, asssumes that all clients are
            # good to use
            self.available_clients = list(range(1, self.n_peers + 1))
            self.all_clients = list(range(1, self.n_peers + 1))
        else:
            self.available_clients = allocated_clients.copy()
            self.all_clients = allocated_clients.copy()

        self.priority = priority
        self.TAG_CLIENT = TAG_CLIENT_NO_PRIO if not self.priority else TAG_CLIENT_PRIO
        self.TAG_SERVER = TAG_SERVER_NO_PRIO if not self.priority else TAG_SERVER_PRIO

        self.outstanding_response = self.comm.irecv(tag=self.TAG_CLIENT)

        self.local_queue = []


    def poll(self, block=True, timeout=None):
        '''
            Attempt to get a response from a client and enqueue it
        '''
        status = False
        response = None
        if block:
            if timeout is None:
                # Unless something fatal happens, this returning means it succeeded
                response = self.outstanding_response.wait()
                status = True
            else:
                timeout_remaining = timeout

                # Busy loop, as MPI does not offer native timeouts
                while timeout_remaining > 0.0:
                    timeout_delay = max(timeout_remaining * QUEUE_TIMEOUT_RATE, 0.05)
                    request_start = time.time()

                    status, response = self.outstanding_response.test()

                    if status:
                        break

                    time.sleep(timeout_delay)

                    timeout_remaining -= time.time() - request_start
        else:
            status, response = self.outstanding_response.test()

        if status:
            client_rank, result = response
            self.available_clients.append(client_rank)
            # Refresh the request object
            self.outstanding_response = self.comm.irecv(tag=self.TAG_CLIENT)
            self.local_queue.append(result)


    def get(self, block=True, timeout=None):
        '''
            Attempt to get a response from a client
        '''
        if self.local_queue:
            return self.local_queue.pop(0)

        self.poll(block, timeout)
        if self.local_queue:
            return self.local_queue.pop(0)

        raise Empty("Queue failed to retrieve an item" + "" if timeout is None else f"within timeout {timeout}")


    def put(self, v, block=True, timeout=None):
        # TODO : Handle blocking behaviour?
        if self.available_clients:
            client_rank = self.available_clients.pop(0)
            self.comm.send(v, dest=client_rank, tag=self.TAG_SERVER)
        else:
            raise Full("No peers available to put the message to")


    def putall(self, v):
        '''
            Sends a message to every client
        '''
        for rank in self.all_clients:
            self.comm.send(v, dest=rank, tag=self.TAG_SERVER)


    def empty(self):
        return not self.local_queue and not self.outstanding_response.get_status()


    def full(self):
        return not self.available_clients


    def qsize(self):
        return len(self.local_queue) + 1 if self.outstanding_response.get_status() else 0



class MPIClientQueue():
    def __init__(self, comm, priority=False):
        '''
            Create the client queue (receives jobs, returns results)
        '''
        self.comm = comm
        self.rank = comm.Get_rank()

        if self.rank == 0:
            raise Exception("Client queue should not be used by MPI root peer")

        self.priority = priority

        self.TAG_CLIENT = TAG_CLIENT_NO_PRIO if not self.priority else TAG_CLIENT_PRIO
        self.TAG_SERVER = TAG_SERVER_NO_PRIO if not self.priority else TAG_SERVER_PRIO


    def get(self, block=True, timeout=None):
        # TODO : Blocking behaviour?
        msg = self.comm.recv(source=0, tag=self.TAG_SERVER)

        return msg


    def put(self, v, block=True, timeout=None):
        # TODO : Blocking as above?
        self.comm.send((self.rank, v), dest=0, tag=self.TAG_CLIENT)


    def empty(self):
        raise NotImplementedError("No meaningful notion of client queue emptiness w/ MPI")


    def full(self):
        raise NotImplementedError("No meaningful notion of client queue fullness w/ MPI")


    def qsize(self):
        raise NotImplementedError("No meaningful notion of client queue size w/ MPI")
