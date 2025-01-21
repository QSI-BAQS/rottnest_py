class Sequencer():
    '''
        Widget Sequencer
    '''
    def __init__(self,
            *architectures,
            sequence_length = 2000
            ):
       
        # Map architectures to proxies 
        self._architecture_proxies = architectures
        self.priority_shim = [] 

        self.sequence_length = sequence_length


    def sequence(self, parser): 

        for ops in zip(parser.parse()):
            if len(self.priority_shim) == 0: 
                yield(ops)

