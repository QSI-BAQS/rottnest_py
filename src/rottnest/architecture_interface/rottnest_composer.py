'''
    Rottnest Composer interface

    This class handles program logic relating
    to the composition of widgets

'''
import abc

from typing import Type

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

        # Layouts
        self.layouts = list(map(LayoutProxy.add_layout, layouts))

        # Memory management system
        self.memory_manager = self.memory_manager_constructor()(self.ResultsComposer)

        # Initial stack frames
        self.setup()

        # TODO : This may be a problem if we ever have composers in parallel
        # (we hopefully shouldn't)
        RottnestComposer.result_cache[RottnestComposer.__START] = self.stack_frames[0]

        # Maps active ids to stack frames
        self.active_compute_units = {}
        self._compute_units = {}
        self._all_submitted = False


    def setup(self, initial_qubits=None):
        '''
            Composer context reset and setup function
            Resets the current result from;
                - The top of the stack (replaced with a fresh stack frame)
                - The start symbol (replaced with the above fresh stack frame)
            This allows safe composer reuse with full cache (minus result entry)
        '''
        if initial_qubits is None:
            # TODO
            # This is not currently used but is a stub
            # for a potential future implementation
            initial_qubits = set()

        initial_frame = self.StackFrame(
                    RottnestComposer.__START,
                    self.ResultsComposer,
                    qubit_map={},
                    memory_manager=self.memory_manager
            )

        self.stack_frames = [initial_frame]
        self.memory_manager.frame_create(
            initial_frame.get_id(),
            initial_qubits
        )

        self._all_submitted = False

        # TODO : Maybe reset cache deferences?

        # TODO : this should hook the instance
        RottnestComposer.result_cache[RottnestComposer.__START] = self.stack_frames[0]

    def submit(self, compute_unit):
        '''
            Submitting a compute unit
        '''
        stack_frame = self.hook_compute_unit(compute_unit)
        stack_frame.submit(compute_unit)
        self.memory_manager.load(stack_frame.get_id(), compute_unit.get_qubit_labels().keys())

        # Hook this one for later
        self._compute_units[compute_unit.unit_id] = compute_unit
        self.memory_manager.free(stack_frame.get_id(), compute_unit.get_measured_qubit_labels())

    def receive(self, result_composer: "ResultsComposer"):
        '''
            Receiving a result from a compilation
        '''
        #result = self.ResultsComposer(result)
        compute_unit_ids = result_composer.get_compute_unit_ids()

        # All units should belong to the same stack frame
        stack_frame = self.unhook_compute_unit(compute_unit_ids[0])

        # Memory management
        for cu_id in compute_unit_ids:
            compute_unit = self._compute_units[cu_id]

            self.memory_manager.idle(
                stack_frame.get_id(),
                result_composer.get_tocks()
            )

            store_labels = (
                set(
                    compute_unit.get_qubit_labels().keys()
                ).difference( 
                    compute_unit.get_measured_qubit_labels()
                )
            )
                 
            self.memory_manager.store(
                stack_frame.get_id(), 
                store_labels
            )
            self._compute_units.pop(cu_id)
        stack_frame.receive(result_composer)

    def cache_entry_start(self, cache_obj):
        '''
            Creates a new stack frame
        '''
        # Store all qubits to create clean cache context

        # TODO: Not completed?
        operation = cache_obj.op

        # Get qubits that are pulled
        # TODO: Not completed?
        input_qubits = operation.qubits

        # Example only
        qubit_map = {}

        # Create new stack frame with loaded qubits
        stack_frame = self.StackFrame(
            cache_obj.cache_hash(),
            self.ResultsComposer,
            qubit_map=qubit_map,
            memory_manager=self.memory_manager
        )

        self.memory_manager.frame_create(
            stack_frame.get_id(),
            input_qubits
        )

        # Prev Frame
        prev_frame = self.stack_frames[-1]

        # Stack frame goes on the bottom
        self.stack_frames.append(stack_frame)

        # Add it to the cache
        RottnestComposer.result_cache[cache_obj.cache_hash()] = stack_frame

    def cache_entry_end(self, cache_obj):
        '''
            Sequencer should provide assertion that this
             function is not called unless all compute
             units for the stack frame are compiled
        '''
        # NOTE: Work around for the meantime
        if self.stack_frames[-1].cache_hash() != cache_obj.cache_hash():
            raise Exception(
                "Received unmatched cache_end in stream",
                cache_obj.cache_hash(),
                self.cache_hash_stack # ty: ignore NOTE: This appears unresolved?
            )

        # Remove frame from stack
        old_frame = self.stack_frames.pop()

        old_frame.last_submitted()

        # Frame hasn't received everything, or possibly has its own deferred cache
        if not old_frame.complete():
            self.stack_frames[-1].register_cache_deference(old_frame)
            self.memory_manager.frame_pop(old_frame.get_id())
        else:
            # Compose into caller
            # TODO: Get labels
            mem_cost = self.memory_manager.frame_delete(old_frame.get_id())

            # Compose costs from memory unit with the frame

            old_frame.parallel_compose(mem_cost)
            self.stack_frames[-1].compose_stack_frames(old_frame)
            # Idle the memory manager's next stack frame
            self.memory_manager.idle(
                self.stack_frames[-1].get_id(),
                old_frame.get_tocks()
            )


    def all_submitted(self):
        '''
            All compute unit objects submitted
        '''
        self._all_submitted = True

        # All jobs for top level stack frame are now outstanding
        self.stack_frames[0].last_submitted()

    def complete(self):
        '''
            Checks if the program is complete
        '''
        # To be complete;
        # - All units have been submitted
        # - The only stack frame left is the top-level frame
        # - The top-level frame is complete
        return self._all_submitted and len(self.stack_frames) == 1 and self.stack_frames[0].complete()

    def get_result(self):
        '''
            Returns result
            This just pulls the top level stack frame
        '''
        return RottnestComposer.result_cache[RottnestComposer.__START].get_result()

    def get_logical_patches(self):
        '''
            Get number of logical patches needed
        '''
        return self.memory_manager.logical_patches()

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
        while None is not (layout := self.get_next_layout()):
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
        if not (cached_frame := RottnestComposer.result_cache[cache_obj.cache_hash()]).complete():
            self.stack_frames[-1].register_cache_deference(cached_frame)
            return False
        else:
            # Compose the cache request result into the active frame
            res_obj = RottnestComposer.result_cache[
                cache_obj.cache_hash()
            ]

            self.stack_frames[-1].compose_stack_frames(
                res_obj
            )
            return res_obj.get_result() 

    def get_memory_manager(self):
        '''
            Memory manager getter
        '''
        return self.memory_manager


class ComposerStackFrame:
    '''
        Stack frame instance for the composer
    '''
    CTR = 0

    def __init__(self,
            rottnest_hash,
            results_composer_constructor: Type,
            qubit_map: dict,
            memory_manager
        ):

        # Tracks current qubits
        self.qubit_map = qubit_map

        self._id = ComposerStackFrame.CTR
        ComposerStackFrame.CTR += 1

        self.rottnest_hash = rottnest_hash
        self.ResultsComposer = results_composer_constructor

        self.memory_manager = memory_manager


        self.result = self.ResultsComposer(CACHED=True) 

        self.all_submitted = False
        self.compilation_complete = False

        self.n_submitted = 0
        self.n_received = 0

        # Number of qubits
        self.n_qubits_in_frame = len(qubit_map)

        # Frames that depend on this frame
        self.parent_frames = set()

        # A map frame -> n for the frames this frame depends on
        self.deferred_frames = dict()

    def get_id(self):
        '''
            Simple unique ID system
        '''
        return self._id

    def complete_parent_deferences(self):
        '''
            Iterate through a frame's registered parents,
            informing them of its completion
        '''
        for parent in self.parent_frames:
            parent.resolve_deferred_child(self)

        self.parent_frames = set()


    def resolve_deferred_child(self, frame):
        '''
            Resolve a child frame's completion, merging it into this frame
        '''
        if frame not in self.deferred_frames:
            raise Exception(f"Cache resolution triggered merging non-child frame {frame.cache_hash()} into {self.cache_hash()}")

        first_instance = True
        # Loop over the number of times this frame is a child
        # Compose each instance
        for i in range(self.deferred_frames.pop(frame)):

            # First instance of a deferred frame, resolve its memory
            if first_instance:
                mem_cost = self.memory_manager.frame_delete(frame.get_id(), [])

                # Compose costs from memory unit with the frame
                frame.parallel_compose(mem_cost)

                # Idle the memory manager's next stack frame
                self.memory_manager.idle(
                    self.get_id(),
                    frame.get_tocks()
                )
                first_instance = False

            self.compose_stack_frames(frame)


        if self.complete():
            self.complete_parent_deferences()

    def register_cache_deference(self, child_frame):
        '''
            Registers a deferred frame with a parent
        '''
        self.deferred_frames[child_frame] = self.deferred_frames.get(child_frame, 0) + 1
        child_frame.parent_frames.add(self)

    def cache_hash(self):
        return self.rottnest_hash

    def get_result(self):
        return self.result


    def parallel_compose(self, other: "Result"):
        '''
            Composes memory results
            This differs from stack frame composition
        '''
        self.get_result().parallel_compose(other)

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
        #self.idle_volume = n_cycles * self.non_participatory_qubits
        #self.memory_unit.idle(n_cycles)

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
            Compute units received that are part of this
            stack frame
        '''
        self.result += result
        self.n_received += result.get_n_compute_units()

        if self.complete():
            self.complete_parent_deferences()

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
                and not self.deferred_frames
            )
        return self.compilation_complete


class MemoryManager:
    '''
        Simple class that tracks the current state of memory
        This is useful for architectures with inhomogeneous memories
        Also useful for separating storage from

        The initial empty construction is identical to an arbitrary
        connectivity between an arbitrary number of devices
        this is not the best model for minimising qubit counts

        Idling costs are accounted by the stack frame management
        To restrict the hypothetical number of
    '''

    def __init__(self, results_composer_constructor):
        '''
            Constructor
        '''
        self.ResultsComposer = results_composer_constructor

    def frame_create(self, frame_id: int, labels: list):
        '''
            Costs memory movement to create a frame context
        '''
        return self.ResultsComposer()

    def frame_pop(self, frame_id: int):
        '''
            Pops frame from memory manager stack without 
            collecting compilation data
        '''

    def frame_delete(self, frame_id: int, labels: list | None = None):
        '''
            Frame context finished
            The labels passed should be preserved, the rest may be dropped
        '''
        return self.ResultsComposer()

    def store(self, frame_id: int, labels: list | None = None) -> None:
        '''
            Costs storing memory
        '''

    def load(self, frame_id: int, labels: list | None = None) -> None:
        '''
            Costs storing memory
        '''

    def idle(self, frame_id: int, n_cycles: int) -> "ResultsComposer":
        '''
            Costs idling for n cycles
        '''
        return self.ResultsComposer()

    def free(self, frame_id: int, labels: set) -> None:
        '''
            Indicates that this memory has been freed
        '''

    def get_logical_patches(self) -> int:
        '''
            Number of logical patches needed so far
        '''
        return 0

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

    # Marks the object as a cache object
    CACHED = 'CACHED'
    CACHED_ARG = 'cached'

    

    def __init__(
            self,
            result_obj: dict | None = None,
            n_obj = 1,
            unit_id = None,
            CACHED = False
            ):
        '''
            Constructor
        '''
        if result_obj is None:
            result_obj = {}
        self._obj = result_obj

        # Used for tracking batching of results
        # TODO : Batching will result in massive
        # lists - provide a way to drop the ids once
        # the result hits cache
        self._unit_ids = []
        if unit_id is not None:
            self._unit_ids.append(unit_id)
        self._n_obj = n_obj

        self._cached = CACHED

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
        # tmp_recv = self._n_obj # NOTE: Does not appear to be used?

        self.__iadd__(other)
        self._unit_ids = tmp_ids
        self._n_obj = other._n_obj

    def parallel_compose(self, other):
        '''
            Composition of operation in parallel
            Useful for memory unit operations
        '''
        pass

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
        args = self._to_args()
        if self._cached:
            args[self.CACHED] = self._cached
        return args

    def _to_args(self):
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

    def get_postprocessing_data(self):
        '''
            Ambit method for retrieving any relevant post-processing data from the
            architecture run
        '''
        raise NotImplementedError

    def to_runchart(self):
        '''
            Converts the object to a format for
            display on the runchart
        '''
        return str(self._obj)

    def get_tocks(self):
        '''
            Gets the number of tocks for this result object
        '''
        raise NotImplementedError("Results composer does not implement a get_tocks method")
