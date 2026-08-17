from typing import Protocol, Tuple, Callable, Any
from enum import Enum
import time
import math


class PollExecutionState:
    '''
       Keeps track of the following details
       * delay
       * timeout
       * elapsed time
       * next_tick
    '''

    def __init__(self, delay: int, timeout: int | None = None):
        '''
           Initialises with delay and timeout 
        '''
        self.delay = delay
        self.timeout = timeout
        self.next_tick: float = 0
        self.first_start_time: float | None = None
        self.start_time: float = 0
        self.end_time: float = 0
        self.last_end_time: float = 0
        self.elapsed_time: float = 0
        self.end_tick: float = 0

    def snapshot_timeout(self) -> float:
        '''
           Computes the total from the first start call,
           if timeout is None or snapshot_start has not been called
           it will return None
        '''
        if self.timeout is None or self.first_start_time is None:
            return math.inf
        else:
            return self.first_start_time + self.timeout

    def snapshot_start(self):
        '''
           Creates a snapshot of the start time 
        '''
        self.start_time = time.time()
        self.first_start_time = self.start_time

    def snapshot_end(self):
        '''
           Creates a snapshot of the end time 
        '''
        self.end_time = time.time()
        self.last_end_time = self.end_time

    def snapshot(self):
        '''
           Computes elapsed time
        '''
        current_elapsed = self.end_time - self.start_time
        self.elapsed_time += current_elapsed
        self.end_time = 0
        self.start_time = 0
        return current_elapsed

    def snapshot_nexttick(self):
        '''
            Computes the next tick calculation using the last end_time
        '''
        last_end_time = self.last_end_time
        self.next_tick = last_end_time + self.delay

    def snapshot_stoptick(self):
        '''
           For 'run-until' mode, it needs to compute the duration
           that it would it would run for 
        '''
        self.end_tick = self.first_start_time + self.delay

    def exceeded_time(self):
        '''
           For 'run-until' mode, it will use last_end_time
           and check to see if it has exceeded end_tick 
        '''
        return self.end_tick < self.last_end_time

    def is_ready(self):
        '''
            Uses the current time to check if the poll is ready to
            execute
        '''
        current_time = time.time()
        next_tick = self.next_tick
        ready = (current_time - next_tick) > 0

        return ready

    def timedout(self):
        '''
           Checks to see if the execution has encountered a timeout 
        '''
        current_time = time.time()
        last_valid_time = self.snapshot_timeout()
        return current_time > last_valid_time
    
class PollExecutionType(Enum):
    '''
       PollExecutionType
       This is used to outline what kind of execution that should
       be supported when running.

       * Auto - This lets the procedure manager decide

       * Immediate - Outlines that the procedure will execute until it is finished

       * ExecuteThenYield - Given a delay known ahead of time, it will execute
           the poll operation and then yield, the finish time is recorded
           
       * ExecuteUntilYield - Given a delay known ahead of time, it will execute
           the poll operation until the timer has been exhausted then yield occurs,
           finish time is recorded and delay used
    '''
    Auto = 0
    Immediate = 1
    ExecuteThenYield = 2
    ExecuteUntilYield = 3
    
    @classmethod
    def make_then_yield(cls, delay: int = 1, timeout: int = 60) -> Tuple['PollExecutionType', int | None, int | None]:
        '''
           Makes a 'then-yield' type that will be used with the procedure
           manager, this is only respected if the procedure manager
           is supports the mechanism - otherwise, poll is treated as immediate
        '''
        return (PollExecutionType.ExecuteThenYield, delay, timeout)
    
    @classmethod
    def make_until_yield(cls, delay: int = 1, timeout: int = 60) -> Tuple['PollExecutionType', int | None, int | None]:
        '''
           Makes a 'until-yield' type that will be used with the procedure
           manager, this is only respected if the procedure manager
           is supports the mechanism - otherwise, poll is treated as immediate
        '''
        return (PollExecutionType.ExecuteUntilYield, delay, timeout)
    
    @classmethod
    def make_immediate(cls) -> Tuple['PollExecutionType', int | None, int | None]:
        '''
            Makes an 'immediate' type that will be used to run the poll
            without pause
        '''
        return (PollExecutionType.Immediate, None, None) 


    @classmethod
    def make_yield_wrapper(cls, kind: 'PollExecutionType',
                           poll_callback,
                           abort_callback,
                           delay: int,
                           timeout: int) -> Callable[[Any], None]:
        '''
            Checks to see what yield variant it is and builds an appropriate
            callback for it.
        '''
        yield_exec_state = PollExecutionState(delay, timeout)
        
        if kind == PollExecutionType.ExecuteThenYield:
            def _exec_then_yield(proc_state):
                'Executes then yields'
                exec_state = yield_exec_state

                if exec_state.timeout():
                    abort_callback()
                    return
                if exec_state.is_ready():
                
                    exec_state.snapshot_start()
                  
                    poll_callback(proc_state)

                    exec_state.snapshot_end()
                    exec_state.snapshot_nexttick()
                else:
                    print("Not ready yet")
                
            return _exec_then_yield
        elif kind == PollExecutionType.ExecuteUntilYield:
            def _exec_until_yield(proc_state):
                'Executes until it should yield'
                exec_state = yield_exec_state

                if exec_state.timeout():
                    abort_callback()
                    return
                
                if exec_state.is_ready():

                    exec_state.snapshot_start()
                    exec_state.snapshot_stoptick()

                    while not exec_state.exceeded_time():

                        poll_callback(proc_state)
                        exec_state.snapshot_end()

                    exec_state.snapshot_nexttick()
                
            return _exec_until_yield 
        return poll_callback

    @classmethod
    def rewrap_for_yieldable(cls, poll_type: 'PollExecutionTuple', poll_callback,
                             abort_callback):
        '''
           Rewraps the poll function if the poll_type is not-immediate
           If immediate, it will just return the poll_callback itself  
        '''
        delay = poll_type[1] if poll_type[1] is not None else 0 
        timeout = poll_type[2] if poll_type[2] is not None else 0
        ptype = poll_type[0]
        if ptype != PollExecutionType.Immediate:
            return PollExecutionType.make_yield_wrapper(ptype, poll_callback,
                                                        abort_callback,
                                                        delay, timeout)
        else:
            return poll_callback
        

PollExecutionTuple = Tuple[PollExecutionType, int | None, int | None]
