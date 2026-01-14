'''
    Handles allocation of a given pool of MPI workers between pandora and rottnest
'''

from abc import ABC, abstractmethod

class MPIWorkerAllocator(ABC):
    def __init__(self, n_peers):
        self.n_peers = n_peers

    @abstractmethod
    def rottnest_workers(self):
        '''
            From a pool of n_peers, choose some to be rottnest workers

            Must return a list of integers in [1, n_peers), with a guarantee
            that the same integers cannot be returned by either of the other allocation
            functions, and that every integer in the interval must be returned by one
            of the three functions

            Must return the same list of integers upon being called again
        '''
        raise NotImplementedError("rottnest_workers is abstract")


    @abstractmethod
    def rottnest_prio_workers(self):
        '''
            As above, but chooses the priority rottnest workers
        '''
        raise NotImplementedError("rottnest_prio_workers is abstract")


    @abstractmethod
    def pandora_workers(self):
        '''
            As above, but chooses the pandora workers
        '''
        raise NotImplementedError("pandora_workers is abstract")


class FixedRatioAllocator(MPIWorkerAllocator):
    def __init__(self, n_peers, ratio):
        if ratio <= 0.0 or ratio >= 1.0:
            raise Exception("Ratio for allocator should be in range (0, 1)")
        self.ratio = ratio
        super().__init__(n_peers)


    def rottnest_workers(self):
        '''
            Allocates workers from the front of the pool, up to the given ratio (rounded down)

            Raises an exception if no workers can be allocated
        '''
        ratio_threshold = int(self.n_peers * self.ratio)
        res = list(filter(
            lambda x: x <= ratio_threshold,
            range(2, self.n_peers)
        ))

        if len(res) == 0:
            raise Exception(f"Was unable to allocate any peers as rottnest workers with ratio {self.ratio}")

        return res


    def rottnest_prio_workers(self):
        '''
            Allocates the very first worker as the prio rottnest worker
        '''
        return [1,]


    def pandora_workers(self):
        '''
            Allocates workers beyond those given to rottnest
        '''
        ratio_threshold = int(self.n_peers * self.ratio)
        res = list(filter(
            lambda x: x > ratio_threshold,
            range(2, self.n_peers)
        ))

        if len(res) == 0:
            raise Exception(f"Was unable to allocate any peers as pandora workers with ratio {1 - self.ratio}")

        return res
