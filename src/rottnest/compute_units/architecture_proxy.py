import abc
import math as maths
from rottnest.region_builder.json_to_region import json_to_layout

# TODO Turn this dependency into a generic interface 
from t_scheduler.region.widget_region import RegionStats 

saved_architectures = {}

'''
    Base class describing an arbitrary collection of computation units
    For example superconducting architectures, ion traps etc 
    A compute unit is a fixed layout that is executed against 

    Supports benchmarking, full compilation and simulation for probabalistic structures
'''

class ArchitectureProxy(object):
    @classmethod
    def check_pregenerated(cls, architecture_id):
        if architecture_id not in saved_architectures:
            raise ValueError(f"Unknown architecture with id {architecture_id}")
 
        return isinstance(saved_architectures[architecture_id], cls)

    def __new__(cls, architecture_id):
        if cls.check_pregenerated(architecture_id):
            return saved_architectures[architecture_id]
        else:
            return object.__new__(ArchitectureProxy)

    def __init__(
        self,
        architecture_id 
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

        if self.check_pregenerated(architecture_id):
            # Skip __init__, we returned an past generated object in __new__
            return

        self.architecture_id = architecture_id 

        self.underlying_json = saved_architectures[architecture_id]

        # We checked in __new__ whether we're pregenerated, so this is the path otherwise
        # Hence saved_architectures contains the raw json under architecture_id
        layout = json_to_layout(self.underlying_json)

        # Now that we've stolen the layout, save ourselves to the mapping
        saved_architectures[architecture_id] = self

        # Generate the layout
        regions, routers = layout.create()

        self.regions = regions
        # self.routers = routers
        
        stats = sum((region.stats for region in regions), start=RegionStats())
        self.stats = stats

        self.num_registers = stats.num_registers() 
        self.num_t_buffers = stats.num_t_buffers()
        self.num_bell_buffers = stats.num_bell_buffers()

        # self.bell_rate = bell_rate
        # self.t_rate = t_rate

    def num_qubits(self):
        return self.num_registers

    def mem_bound(self): 
        '''
            Over-rideable method
        '''
        return self.num_registers

    def to_json(self):
        return self.underlying_json

    def benchmark(self, computation): 
        pass

    def set_t_rate(self, t_rate):
        self.t_rate = t_rate

    def _eps_to_t_count(self, eps):
        '''
        Simple heuristic for t count for fixed epsilon 
        '''
        return maths.ceil(10 + 4 * maths.log2(1 / eps))

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
