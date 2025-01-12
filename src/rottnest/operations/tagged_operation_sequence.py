from rottnest.operations.operation_tag import OperationTag 

class OperationSequenceFactory(OperationTagFactory):
    '''
        OperationSequenceFactory
        Simple example, takes an operation 
        sequence, splits and tags it

        Ownership of the sequence should be 
        retained by this object.


        The rz_limit may be inhomogeneous 

        TODO: Eventually this is going to end up
        turning into a scheduler class over 
        a set of connected compute units 
        For now we just assume a single linear
        connection. 
    '''
    def __init__(self, operation_sequence, *rz_limits):
        self.sequence = operation_sequence
        self.rz_limits = rz_limits

    def __iter__(self):
        pass


def OperationSequenceTag(OperationTag):
    def __init__(self, start, end):
        
