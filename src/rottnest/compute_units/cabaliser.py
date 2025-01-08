from cabaliser import gates
from cabaliser.operation_sequence import OperationSequence 
from cabaliser.widget_sequence import Widget

import numpy as np

# Replace with appropriate types
OperationTag = type("OperationTag", tuple(), dict())
Architecture = type("Architecture", tuple(), dict())


# TODO: Transformer classes for operations

# Code widgets are not equivalent to widgets 
class ComputationUnit(SharedRNG):
    '''
        Splices ops into computation units
        Only a single computation units should exist in memory at a time
    ''' 

    def __init__(self, ops, *compute_units, **kwargs):
        self.computation_units 
        self.computed_widgets = list()

        # Pass generator if appropriate
        super().__init__(**kwargs)
         

    def compile(): 
        pass
   
 
 
class ComputedWidget(SharedRNG):  
    def __init__(
        self,
        tag_fn: OperationTag ,
        target_arch: Architecture,
        seed=0):
    
        self.start = start
        self.stop = stop
        self.target_arch = target_arch

        self.volume = 0 
        self.err = 0 
        self.max_decoder = 0
        self.avg_decoder = 0

    def compile(ops): -> Widget
        wid = Widget(width, self.max_qubits)

        del wid
        
        # Do not wait for the garbage collector thread, force this
        gc.collect()
