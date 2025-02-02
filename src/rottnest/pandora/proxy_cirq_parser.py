from cabaliser.operation_sequence import OperationSequence

class ProxyCirqParser:
    '''
        This object proxies a cirq parser
    '''

    def __init__(self, op_seq, memory):
        self.op_seq = op_seq
        self.memory = memory
        self.fully_decomposed = True
        
    def __len__(self):
        '''
            Returns memory in use
        '''
        return memory

    def cache_hash(self): 
        return None

    def reset_context():
        pass

    def extract_context():
        pass

    def parser():
        yield self.op_seq

    def decompose(self):
        return iter(self)

    def parse(self):
        '''
        Pandora objects require no parsing
        '''
        pass
