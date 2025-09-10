'''
    Adapter class for mapping Rz gates to tags 
'''
from rottnest.gridsynth.gridsynth import DEFAULT_PRECISION
from rottnest.rz_decomposer.angle_to_rational import angle_to_rational 

from cabaliser.gate_constructors import MEASUREMENT_GATE_TAG 


class RzTagTracker():

    #_gs = gridsynth.GridSynth()
    '''
        Maps angles to tags
        TODO: This currently makes some very rough
        assumptions that no two gates will have
        the same angle and differing values of eps 
    '''
    def __init__(self, default_eps = DEFAULT_PRECISION):
        # Reserve tag 0 
        self._angles_to_tags = {None: None}
        self._tags_to_angles = [None] 
        self._eps = [None] 
        self.n_rz_gates = 0
    
        self.default_eps = default_eps

    def __getitem__(self, tag):
        return self._tags_to_angles[tag]

    def get_gridsynth_params(self, tag):
        '''
            Helper function to turn a tag into a rz_decomposer input
        '''
        if tag == MEASUREMENT_GATE_TAG:
            # Measurement gate tag
            angle = 0
            eps = 10
        else:
            eps = self._eps[tag]
            if eps is None:
                eps = self.default_eps
            else:
                eps = max(eps, self.default_eps)

            angle = self._tags_to_angles[tag]

        angle = angle % 2

        if eps is None: 
            eps = self.default_eps 
        p, q = angle_to_rational(angle, precision=eps)
        return p, q, eps 

    def get(self, angle, eps): 
        '''
        Attempting to get a label is bound to allocating one
        '''
        # Get is triggered by adding an RZ gate
        self.n_rz_gates += 1
        print("RZ:", angle, eps)

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
        return self.__repr__()

    def __repr__(self):
        return super().__repr__()
