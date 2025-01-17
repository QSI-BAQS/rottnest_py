'''
    Handlers for qualtran functions
'''
from functools import partial 

import qualtran
import qualtran.bookkeeping


def arbitrary_clifford():
    '''
        Worst case N qubit clifford
    '''
    def _wrap(
        self,
        operation_sequence: OperationSequence,
        qubit_labels: QubitLabelTracker,
        rz_tags: QubitLabelTracker):
        
        # Replace this with an n qubit arb cliff 
        for i in range(0, self.n, 2): 
            operation_sequence.append(
                cabaliser.gates.CNOT,
                (0, 1) # Get targets
            )

def blank():
    def _wrap():
        pass
    return _wrap

qualtran_ops = {
    bookkeeping.join.Join: blank,
    bookkeeping.split.Split: blank,
    bookkeeping.arbitrary_clifford.ArbitraryClifford: arbitrary_clifford
}
