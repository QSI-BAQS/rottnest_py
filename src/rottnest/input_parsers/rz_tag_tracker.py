'''
    Adapter class for mapping Rz gates to tags 
'''


class RzTagTracker():

    #_gs = gridsynth.GridSynth()
    '''
        Maps angles to tags
        TODO: This currently makes some very rough
        assumptions that no two gates will have
        the same angle and differing values of eps 
    '''
    def __init__(self):
        # Reserve tag 0 
        self._angles_to_tags = {None: None}
        self._tags_to_angles = [None] 
        self._eps = [0] 
        self.n_rz_gates = 0

    def __getitem__(self, tag):
        return self._tags_to_angles[tag]

    def get(self, angle, eps): 
        '''
        Attempting to get a label is bound to allocating one
        '''
        # Get is triggered by adding an RZ gate
        self.n_rz_gates += 1

        tag = self._angles_to_tags.get(angle, None)
        if tag is None: 
            tag = len(self._angles_to_tags)
            self._angles_to_tags[angle] = tag 
            self._tags_to_angles.append(angle)
            self._eps.append(eps)
        return tag 
    
    def reset(self):
        '''
            Context for the tracker is reset
        '''
        self.n_rz_gates = 0

    def decompose_tag(self, tag, eps=None):
        pass
        #rz = self.get()         

    def gets(self, *angles):
        return tuple(map(self.get, angles))

    def len(self):
        return len(self.labels)

    def __str__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()
