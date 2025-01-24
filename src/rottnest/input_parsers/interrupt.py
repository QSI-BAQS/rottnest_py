class INTERRUPT:
    '''
        This is an interrupt class for chucking into streams of cirq moments 
        It iters into itself, and evaluates against itself 
        This means that it acts as a cirquit, a moment and an operator and can be caught
        at all three levels
    '''

    def __iter__(self):
        yield self 

    def __hash__(self):
        return id(INTERRUPT)

    def __eq__(self, other):
        return hash(self) == hash(other) 
