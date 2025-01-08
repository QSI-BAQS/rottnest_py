import abc
import math as maths

class ComputeUnit(abc.ABC):

    def __init__(
        self,
        bell_rate: float,
        t_rate: float,
        register_max: int,
        t_buffer_max: int,
        bell_buffer_max : int):
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
        self.bell_rate = bell_rate
        self.t_rate = t_rate
        self.register_max = register_max
        self.t_buffer_max = t_buffer_max
        self.bell_buffer_max = bell_buffer_max

    def _eps_to_t_count(self, eps):
        '''
        Simple heuristic for t count for fixed epsilon 
        '''
        return maths.ceil(10 + 4 * maths.log2(1 / eps))

    def stage_1(self, n_registers=None: int):
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
            n_registers = self.register_max

    def _calc_rz_limit(
        self,
        n_reg: int,
        eps: float,
        overclock_rate: float = 1):
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
        # Time to generate bell states
        bell_input_time = maths.ceil(n_reg / bell_rate)
        graph_construction_time = 2 * n_reg   

        stage_1 = max(bell_input_time, graph_construction_time)

        # Time to pass inputs to graph 
        stage_2 = 2 * n_reg 
        
        # Number of T gates expected in first
        # two stages
        t_gen = (stage_1 + stage_2) * t_rate

        n_rz_gates = maths.ceil(self.overclock_rate * t_get / self._eps_to_t_count(eps))
        return n_rz_gates
