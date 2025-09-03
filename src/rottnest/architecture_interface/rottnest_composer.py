'''
    Rottnest Composer interface

    This class handles program logic relating 
    to the composition of widgets

'''
import abc
from collections import defaultdict

from typing import Type
from types import GeneratorType

class RottnestComposer(abc.ABC):
    '''
        Handles composition of compilation units 
    '''

    @staticmethod
    def results_composer_constructor() -> Type["ResultsComposer"]:
        '''
            Dispatch method for modular hooking of constructors 
        '''
        return ResultsComposer

    @staticmethod
    def stack_frame_constructor() -> Type["ComposerStackFrame"]:
        '''
            Dispatch method for modular hooking of constructors 
        '''
        return ComposerStackFrame

    @staticmethod
    def memory_manager_constructor() -> Type["MemoryManager"]:
        '''
            Dispatch method for modular hooking of constructors
        '''
        return MemoryManager


    def __init__(self, layouts, qubits):

        # Tracks qubits irrespective of renaming
        self.qubit_map = {qubit:i for i, qubit in enumerate(qubits)}

        self.ResultsComposer = self.results_composer_constructor()
        self.StackFrame = self.stack_frame_constructor()

        self.memory_manager = self.memory_manager_constructor()(self.ResultsComposer)

        #context_stack = [self.context_manager()]

        self.layouts = layouts 

        # Traces ownership of qubits through the stack 
        self.qubit_map_stack = []

        # Current stack frames 
        self.stack_frames = []

        # Maps active ids to compute units 
        active_compute_units = {} 

        # Map of hashes to result objects
        self.result_cache = {}

        # Tracks non-participatory qubits for a given stack frame 
        self.non_participatory_stack = [0]
        self.cache_hash_stack = [None]
        self.compute_unit_result_cache = defaultdict(dict)

        # Global Result
        #current_result = self.ResultsComposer()

    def cache_entry_start(self, cache_obj):
        '''
            Creates a new stack frame
            This is used for both caching  
        '''
      
        operation = cache_obj.op
        input_qubits = operation.qubits
        internal_scope = operation.gate.all_qubits()

        qubit_map = {self.stack_frame[-1].qubit_map[qubit] for qubit in input_qubits}
        self.mem_load(input_qubits)
 
        stack_frame = self.StackFrame()

        self.cache_hash_stack.append(
            cache_obj.cache_hash()
        )

        self.non_participartory_stack.append(
            cache_obj.non_participatory_qubits
        )

    def cache_entry_end(self, cache_ob):
        if self.cache_hash_stack[-1] != cache_obj.cache_hash():
            raise Exception(
                "Received unmatched cache_end in stream",
                cache_obj.cache_hash(),
                self.cache_hash_stack
            )
            
        cache_hash = self.cache_hash_stack.pop()
        non_participatory = self.non_participatory_stack.pop()


    def get_layout(self) -> int | object:
        '''
            Gets the id of the next layout to use 
            Allows for inhomogeneous architectures
            May also return a WAIT signal, indicating that
            there are currently no active nodes  
            WAIT is currently not implemented

            TODO: cycle default implementation
        '''
        return 0
       
    def hook_compute_unit(self, unit_id, compute_unit):
        '''
            Sets up tracking of active compute units 
            This allocates the result to the correct stack frame
        '''
        current_stack_frame = len(self.stack_frames) 
        self.active_compute_units[unit_id] = current_stack_frame 

    def compose_result(self, unit_id, result):
        '''
            Composes results and tracks unit ids
            Default implementation reduces
            More complex implementations may do active management of these IDs and layouts 
        '''
        stack_frame = self.active_compute_units[unit_id]
        result = self.results_composer_constructor(result)

        # Pass to both the stack frame, and the global total 
        self.stack_frames[stack_frame].compose_result(result)
        self.active_compute_units.pop(unit_id)


    def cache_request(self, cache_obj) -> bool:
        '''
            Requests an element from the cache
            Returns true if success, false if blocking on previously submitted compute units
        '''
        if self.compute_unit_counts[cache_hash] != self.compute_unit_totals[cache_hash]:
            return False
        
        output = deepcopy(self.compute_unit_result_cache[cache_hash])

        duration = output.n_tocks()

        output['cache_hash_hex'] = cache_hash.hex()
        # print("output:", output, self.compute_unit_counts, self.compute_unit_totals)
        self.manager_completion_queue.put(output)

        tock_dict = output.get('tocks', {})
        np_dur = tock_dict.get('bell', 0) + tock_dict.get('t_schedule', 0) + tock_dict.get('bell2', 0)
        if 'volumes' not in output:
            output['volumes'] = {}

        old_volume = output['volumes'].get('NP_VOLUME', 0) 
        output['volumes']['NP_VOLUME'] = old_volume + np_qubits * np_dur

        for i,stack_hash in enumerate(reversed(self.cache_hash_stack)):
            iadd_result_dicts(
                self.compute_unit_result_cache[stack_hash], output
            )
            output['volumes']['NP_VOLUME'] += self.np_stack[-i-1] * np_dur

        output['volumes']['NP_VOLUME'] = old_volume

        # print(sum(self.np_stack, start=np_qubits), self.compute_unit_result_cache[None]['volumes']['NP_VOLUME'], self.compute_unit_result_cache[None]['tocks']['total'])

        return True


class ComposerStackFrame:
    '''
        Stack frame instance for the composer
    '''

    def __init__(self, 
            rottnest_hash,
            results_composer_constructor: Type,
            qubit_map: dict,
            
        ):

        # Tracks current qubits
        self.qubit_map = qubit_map 

        self.rottnest_hash = rottnest_hash
        self.ResultsComposer = results_composer_constructor

        self.result = self.ResultsComposer() 


class MemoryManager:
    '''
        Simple class that tracks the current state of memory
        This is useful for architectures with inhomogeneous memories 

        The initial empty construction is identical to an arbitrary
        connectivity between an arbitrary number of devices 

        Idling costs are accounted by the stack frame management
        To restrict the hypothetical number of   
    '''
    
    def __init__(self, results_composer_constructor):
        '''
            Constructor
        '''
        self.ResultsComposer = results_composer_constructor

    def load_operation(self, indices: list):
        '''
            Costs loading memory
        '''
        return self.ResultsComposer()

    def store_operation(self, indices: list):
        '''
            Costs storing memory
        '''
        return self.ResultsComposer()


class ResultsComposer:
    '''
        Composition object for composing results
        Technically only requires:
        __add__   :: Composition under addition 
        __iadd__  :: In place addition
        serialise :: Maps to a front-end readable form 
        get_tocks :: Required for non-participatory qubits 

        This is a default implementation and should be 
         overwritten by the architecture module
        
        This assumption assumes that the backing is a
        dictionary of objects where values composer under
         addition 
    '''

    def __init__(self, result_obj: dict):
        '''
            Constructor
        '''
        self._obj = result_obj 
    
    def __iadd__(self, other):
        for key, val in other.items():
            res._obj[key] = res._obj.get(key, 0) + val 

    def __add__(self, other):
        res = ResultsComposer(**self._obj)
        for key, val in other.items():
            res._obj[key] = res._obj.get(key, 0) + val 
        return res

    def serialise(self):
        '''
            Returns a representation for display on the 
              front end
        '''
        return str(self._obj)

    def get_tocks():
        '''
            Gets the number of tocks for this result object
        '''
        raise NotImplementedError("Results composer does not implement a get_tocks method")
