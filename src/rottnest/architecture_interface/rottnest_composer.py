'''
    Rottnest Composer interface

    This class handles program logic relating
    to the composition of widgets

'''
import abc
from collections import defaultdict

from typing import Type
from types import GeneratorType

from itertools import cycle

from rottnest.compute_units.layout_proxy import LayoutProxy

class RottnestComposer(abc.ABC):
    '''
        Handles composition of compilation units
    '''

    __START = object()

    # Map of hashes to result objects
    result_cache = dict()

    @staticmethod
    def results_composer_constructor() -> Type["ResultsComposer"]:
        '''
            Dispatch method for modular hooking
            of constructors
        '''
        return ResultsComposer

    @staticmethod
    def stack_frame_constructor() -> Type["ComposerStackFrame"]:
        '''
            Dispatch method for modular hooking
            of constructors
        '''
        return ComposerStackFrame

    @staticmethod
    def memory_manager_constructor() -> Type["MemoryManager"]:
        '''
            Dispatch method for modular hooking
            of constructors
        '''
        return MemoryManager


    def __init__(self, layouts, qubits):
        # Tracks qubits irrespective of renaming
        self.qubit_map = {qubit:i for i, qubit in enumerate(qubits)}

        # Set dynamic constructors
        self.ResultsComposer = self.results_composer_constructor()
        self.StackFrame = self.stack_frame_constructor()

        # Memory management system
        self.memory_manager = self.memory_manager_constructor()(self.ResultsComposer)

        # Layouts
        self.layouts = list(map(LayoutProxy.add_layout, layouts))

        # Initial stack frames
        # Top level frame has a cache hash of __START
        self.stack_frames = [
            self.StackFrame(
                RottnestComposer.__START,
                self.ResultsComposer,
                qubit_map={}
            )
        ]

        # TODO : This may be a problem if we ever have composers in parallel
        # (we hopefully shouldn't)
        RottnestComposer.result_cache[RottnestComposer.__START] = self.stack_frames[0]

        # Maps active ids to stack frames
        self.active_compute_units = {}


    def reset_result(self):
        '''
            Resets the current result from;
                - The top of the stack (replaced with a fresh stack frame)
                - The start symbol (replaced with the above fresh stack frame)
            This allows safe composer reuse with full cache (minus result entry)
        '''
        self.stack_frames[0] = self.StackFrame(
            RottnestComposer.__START,
            self.ResultsComposer,
            qubit_map={}
        )

        RottnestComposer.result_cache[RottnestComposer.__START] = self.stack_frames[0]


    def submit(self, compute_unit):
        '''
            Submitting a compute unit
        '''
        stack_frame = self.hook_compute_unit(compute_unit)
        stack_frame.submit(compute_unit)

    def receive(self, result_composer: "ResultsComposer"):
        '''
            Receiving a result from a compilation
        '''
        if result_composer.end_computation():
        #    # TODO set pending remaining compute units
            return

        #result = self.ResultsComposer(result)
        compute_unit_ids = result_composer.get_compute_unit_ids()

        print("UNIT IDs", compute_unit_ids)

        # All units should belong to the same stack frame
        stack_frame = self.unhook_compute_unit(compute_unit_ids[0])
        stack_frame.receive(result_composer)

    def cache_entry_start(self, cache_obj):
        '''
            Creates a new stack frame
        '''

        # Store all qubits to create clean cache context
        self.memory_manager.store_all()

        operation = cache_obj.op

        # Get qubits that are pulled
        input_qubits = operation.qubits

        # Example only
        qubit_map = {}
        #qubit_map = {self.stack_frames[-1].qubit_map[qubit] for qubit in input_qubits}
        #self.mem_load(input_qubits)

        # Create new stack frame with loaded qubits
        stack_frame = self.StackFrame(
            cache_obj.cache_hash(),
            self.ResultsComposer,
            qubit_map=qubit_map
        )

        # Prev Frame
        prev_frame = self.stack_frames[-1]
        prev_frame.non_participatory_qubits += cache_obj.non_participatory_qubits

        # Stack frame goes on the bottom
        self.stack_frames.append(stack_frame)

        # Add it to the cache
        RottnestComposer.result_cache[cache_obj.cache_hash()] = stack_frame

    def cache_entry_end(self, cache_obj):
        '''
            Sequencer should provide asser that this function is not
            called unless all compute units for the stack frame are
            compiled
        '''
        if self.stack_frames[-1].cache_hash() != cache_obj.cache_hash():
            raise Exception(
                "Received unmatched cache_end in stream",
                cache_obj.cache_hash(),
                self.cache_hash_stack
            )

        # Remove frame from stack
        old_frame = self.stack_frames.pop()

        old_frame.last_submitted()

        # Compose into caller
        self.stack_frames[-1].compose_stack_frames(old_frame)


    def get_result(self):
        '''
            Returns result
            This just pulls the top level stack frame
        '''
        return RottnestComposer.result_cache[RottnestComposer.__START].get_result()

    def get_next_layout(self) -> int | object:
        '''
            Gets the id of the next layout to use
            Allows for inhomogeneous architectures
            May also return a WAIT signal, indicating that
            there are currently no active nodes
            WAIT is currently not implemented

            Default implementation is to return the first layout
        '''
        return LayoutProxy(self.layouts[0])

    def layout_sequence_generator(self) -> int | object:
        '''
            Generator over get next layout
            Used by the sequencer
        '''
        while None != (layout := self.get_next_layout()):
            yield layout

    def hook_compute_unit(self, compute_unit):
        '''
            Sets up tracking of active compute units
            This allocates the result to the correct stack frame
        '''
        current_stack_frame = self.stack_frames[-1]
        self.active_compute_units[compute_unit.unit_id] = current_stack_frame
        return current_stack_frame

    def unhook_compute_unit(self, compute_unit_id):
        '''
            Unsets tracking of compute unit
        '''
        return self.active_compute_units.pop(compute_unit_id)

    def compose_result(self, unit_id, result):
        '''
            Composes results and tracks unit ids
            Default implementation reduces
            More complex implementations may do active management of these IDs and layouts
        '''
        result = self.results_composer_constructor()(
            result,
            unit_id = unit_id
        )
        return result

    def cache_request(self, cache_obj) -> bool:
        '''
            Requests an element from the cache
            Returns true if success, false if blocking on previously submitted compute units
        '''
        if not RottnestComposer.result_cache[cache_obj.cache_hash()].complete():
            return False

        # Compose the cache request result into the active frame
        self.stack_frames[-1].compose_stack_frames(RottnestComposer.result_cache[cache_obj.cache_hash()])

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

        self.all_submitted = False
        self.compilation_complete = False

        self.n_submitted = 0
        self.n_received = 0

        # Number of qubits
        self.n_qubits_in_frame = len(qubit_map)

        # Qubits that are not passed to a called function
        self.non_participatory_qubits = 0
        self.idle_volume = 0

    def cache_hash(self):
        return self.rottnest_hash

    def get_result(self):
        return self.result

    def compose_stack_frames(self, other: "ComposerStackFrame"):
        '''
            Composes stack frames
        '''
        self.idle(other.get_tocks())
        self.non_participatory_qubits = 0
        self.get_result().compose(other.get_result())

    def idle(self, n_cycles):
        '''
            Adds idle volume to this stack frame
        '''
        self.idle_volume = n_cycles * self.non_participatory_qubits

    def get_tocks(self):
        '''
            Gets the runtime of this stack frame
        '''
        return self.get_result().get_tocks()

    def submit(self, compute_unit, n_submitted=1):
        '''
            Compute units submitted that are part of this stack frame
        '''
        self.n_submitted += n_submitted
        self.qubit_map |= compute_unit._qubit_labels
        self.n_qubits_in_frame = len(self.qubit_map)

    def receive(self, result):
        '''
            Compute units received that are part of this stack frame
        '''
        self.result += result
        self.n_received += result.get_n_compute_units()

    def last_submitted(self):
        '''
            Last submitted
        '''
        self.all_submitted = True

    def complete(self) -> bool:
        '''
            Checks if the compilation of this stack frame is complete
            At that point it can be used as a cache element
        '''
        if not self.compilation_complete:
            self.compilation_complete = (
                self.all_submitted 
                and self.n_submitted == self.n_received
            )
        return self.compilation_complete


class MemoryManager:
    '''
        Simple class that tracks the current state of memory
        This is useful for architectures with inhomogeneous memories
        Also useful for separating storage from

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

    def store_all(self):
        '''
            Stores all qubits
        '''
        pass

    def store_operation(self, indices: list):
        '''
            Costs storing memory
        '''
        return self.ResultsComposer()

    def idle(self, n_cycles: int) -> "ResultsComposer":
        '''
            Costs idling for n cycles
        '''


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

    # A useful symbol
    END_COMPUTATION = 'END_COMPUTATION'

    def __init__(
        self,
        result_obj: dict = None,
        n_obj = 1,
        unit_id = None,
        end_computation = False
        ):
        '''
            Constructor
        '''
        if result_obj is None:
            result_obj = {}
        self._obj = result_obj

        # Used for tracking batching of results
        self._unit_ids = []
        if unit_id is not None:
            self._unit_ids.append(unit_id)
        self._n_obj = n_obj

        self._end_computation = end_computation

    def end_computation(self):
        '''
            End computation getter
        '''
        return self._end_computation

    def items(self):
        return self._obj.items()

    def __iadd__(self, other):
        self._unit_ids += other._unit_ids
        self._n_obj += other._n_obj

        for key, val in other.items():
            self._obj[key] = self._obj.get(key, 0) + val
        return self

    def __add__(self, other):
        res = ResultsComposer(**self._obj)
        for key, val in other.items():
            res._obj[key] = res._obj.get(key, 0) + val

        res._unit_ids = self._unit_ids + other._unit_ids
        res._n_obj = self._n_obj + other._n_obj
        return res

    def get_compute_unit_ids(self):
        '''
            Unit ID getter
        '''
        return self._unit_ids

    def compose(self, other):
        '''
            Unlike addition we use composition to
            imply that one stack frame is
            contained within another
        '''
        tmp_ids = self._unit_ids
        tmp_recv = self._n_obj

        self.__iadd__(other)
        self._unit_ids = tmp_ids
        self._n_obj = other._n_obj

    def get_n_compute_units(self):
        '''
        '''
        return max(len(self._unit_ids), self._n_obj)

    def to_args(self):
        '''
            Emits constructor arguments
            Should be paired with from_args such that:
            self.__class__.from_args(self.to_args()) == self
        '''
        raise NotImplementedError

    @staticmethod
    def from_args(self, *args, **kwargs):
        '''
            Constructor from args
            Rebuilds the class instance over a serial interface
        '''
        raise NotImplementedError

    def serialise(self):
        '''
            Returns a representation for display
            on the front end
        '''
        return str(self._obj)

    def get_tocks(self):
        '''
            Gets the number of tocks for this result object
        '''
        raise NotImplementedError("Results composer does not implement a get_tocks method")
