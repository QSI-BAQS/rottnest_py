import abc
import math as maths

'''
    Base class describing an arbitrary collection of computation units
    For example superconducting architectures, ion traps etc 
    A compute unit is a fixed layout that is executed against 

    Supports benchmarking, full compilation and simulation for probabalistic structures
'''

class ArchitectureProxy():

    def __init__(
        self,
        json_obj
        ):
        '''
            Comput Unit Constructor
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
        self.json = json_obj
        self.arch = None # TODO: generate architecture
        #self.bell_rate = bell_rate
        #self.t_rate = t_rate

        #self.num_registers = register_max
        #self.num_t_buffers = t_buffer_max
        #self.num_bell_buffers = bell_buffer_max

    def benchmark(self, computation: Computable): 
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
