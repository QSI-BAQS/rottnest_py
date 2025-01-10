# Used for annotating classes that take themselves as arguments
from __future__ import annotations

import numpy as np

class SharedRNG:
    '''
        Shared RNG Object
    '''
    def __init__(self,
            generator: SharedRNG = None,
            seed: int = 0):
        '''
        Constructor
        :: generator : SharedRNG :: Generator object if shared 
        :: seed : int :: Seed if not shared generator 
        '''
        self.seed = seed
        if generator is None:
            generator = np.random.default_rng(seed) 
        else:
            generator = generator._generator
        self._generator = generator

    def rng_uniform(self, *args, **kwargs): 
        '''
        rng_uniform
        Generated a uniform random number using the shared generator
        '''
        self._generator.uniform(*args, **kwargs)

    def regenerate(self, seed=None):
        '''
            Updates the RNG generator
            This allows for regeneration of random circuit elements
        '''
        if seed is None:
            seed = self.seed + 1
        self.seed = seed

        self._generator = np.random.default_rng(self.seed)
