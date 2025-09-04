'''
    Proxy class for managing layouts 
'''

import abc
from typing import Generator

import math as maths

class LayoutProxy:
    '''
        This class does an interesting double shift
        The first is as an interface for a singleton cache
        of saved layouts 
        The second is as an interface wrapper for the json
        object stored in the cache, with a particular 
        emphasis in providing a translation layer for
        the composer 

        Architecture load will trigger a monkeypatch
         on the instance of this class in the current
         process

        This generic form is exposed to the workers
    '''

    # Singleton layout cache
    curr_layout_id = 0

    # Singleton json cache 
    saved_layouts = {}

    # Singleton proxy cache 
    saved_proxies = {}

    @classmethod
    def add_layout(cls, layout):
        '''
            Adds a layout, id is incremented
            Should be used as a single source of truth, then ids 
             passed to subprocesses
            `curr_layout_id` is not guaranteed to be synchronous 
             between processes
        '''
        layout_id = cls.curr_layout_id
        cls.saved_layouts[layout_id] = layout
        cls.curr_layout_id += 1
        return layout_id 

    @classmethod
    def add_layout_with_id(cls, layout_id, layout):
        '''
            Binds a layout to a given id
            Should be used for 
        '''
        cls.saved_layouts[layout_id] = layout

    @classmethod
    def get_layouts(cls) -> Generator:
        '''
            Gets all layouts
        '''
        return cls.saved_layouts.items()

    @classmethod
    def get_layout(cls, layout_id) -> dict:
        return cls.saved_layouts.get(layout_id, None)

    @classmethod
    def check_pregenerated(cls, layout_id):
        if layout_id not in cls.saved_layouts:
            raise ValueError(f"Unknown layout with id {layout_id}")
        return layout_id in cls.saved_proxies

    def __new__(cls, layout_id):
        if cls.check_pregenerated(layout_id):
            return cls.saved_proxies[layout_id]
        else:
            return object.__new__(LayoutProxy)

    def __init__(
        self,
        layout_id 
        ):
        '''
            Compute Unit Constructor
            :: bell_rate : float :: Number of bell states generated per toc for one interface 
            :: t_rate : float :: Average number of T states generated per toc 
            :: reg_max : int :: Maximum number of allocatable registers
            :: t_buffer_max : int :: Maximum number of bufferable T states 
            :: bell_buffer_max : int :: Maximum number of bufferable Bell states 

            Given factory warm up times, t_rate should be calculated including the warm up period   
            The rate should be calculated over the stage 1 and stage 2 times 
            The rate should be capped at t_buffer_max

            TODO: More complex, but forward speculating some diminishing number of additional T
            gates generated during stage 3 
        '''

        if self.check_pregenerated(layout_id):
            # Skip __init__, we returned an past generated object in __new__
            return

        # TODO: replace arch_id with layout_id

        self.layout_id = layout_id 
           
        from rottnest.plugins import architectures 
        arch_module = architectures.get_current_architecture()       

        self.stats = arch_module.designer().get_stats(
            self.to_json() 
        ) 

        # Now that we've stolen the layout, save ourselves to the mapping
        LayoutProxy.saved_proxies[layout_id] = self

        # TODO: Fix this
        self.num_registers = self.stats.num_registers 
        #self.num_t_buffers =  self.stats.num_t_buffers
        #self.num_bell_buffers = self.stats.num_bell_buffers

        # self.bell_rate = bell_rate
        # self.t_rate = t_rate

    def num_qubits(self):
        return self.num_registers

    def mem_bound(self): 
        '''
            Maximum number of elements in the graph
        '''
        return self.num_registers

    def to_json(self):
        return LayoutProxy.get_layout(self.layout_id)

    def set_t_rate(self, t_rate):
        self.t_rate = t_rate

    def _eps_to_t_count(self, eps):
        '''
        Simple heuristic for t count for fixed epsilon 
        '''
        return maths.ceil(10 + 4 * maths.log2(1 / eps))


    # TODO:
    # Move these to the composer or delete them
    def stage_1(self, n_registers: int = None):
        '''
        Time required for stage 1 of the pipeline
        During this stage we perform: 
            Graph state construction to completion 
            Input Bell state Generation to completion
        Simultaneously:
            T factories are run and buffered 

            If the Bell state has a buffer max then we need to swap into on the fly generation
            for the second stage
        '''
        if n_registers is None:
            n_registers = self.num_registers
        return max(2 * n_registers, maths.ceil(n_registers / self.bell_rate)) 

    def stage_2(self, n_registers: int = None): 
        '''
            Completes when IO written in 
        '''
        if n_registers is None:
            n_registers = self.num_registers
        return 2 * n_registers 

    @abc.abstractmethod
    def approx_rz_limit(
        self,
        eps,
        n_registers: int = None,
        overclock_rate: float = 1,
        pre_warm = 0):
        '''
            Approximates the RZ limit
            Whereas the calc function runs a simulation to evaluate a reasonable RZ rate, 
            this function instead performs a speculative guess as to the number of T gates 
            based on factories and pre-warm 

            UNUSED
        '''
        pass

    @abc.abstractmethod
    def simulate_rz_limit(
        self,
        eps,
        n_registers: int = None,
        overclock_rate: float = 1,
        pre_warm = 0):
        '''
            Simulates the RZ limit
            Whereas the calc function runs a simulation to evaluate a reasonable RZ rate, 
            this function instead performs a speculative guess as to the number of T gates 
            based on factories and pre-warm 

            UNUSED
        '''
        pass

    def calc_rz_limit(
        self,
        eps: float,
        n_registers: int = None,
        overclock_rate: float = 1,
        pre_warm = 0):
        '''
            Calculates the cap on rz gates for this 
            computation unit. 

            This is to ensure bounded pre-warming, and consistent pipelining 

            :: n_reg : int :: Number of registers
            :: eps : float :: Accuracy of Rz gates  
            :: overclock_rate : float :: Leeway on  

            TODO: This should be parameterised 

            TODO: Forcing order of inputs may provide speedups   
            TODO: Dequeue inputs from register block, double up with teleported bells    
        ''' 
        # Number of T gates expected in first two stages
        t_gen = self.t_rate * (
            self.stage_1(n_registers=n_registers) + 
            self.stage_2(n_registers=n_registers))

        # Ceil rather than floor as if this is zero then we're in trouble
        n_rz_gates = maths.ceil(overclock_rate * t_gen / self._eps_to_t_count(eps))
        return n_rz_gates
