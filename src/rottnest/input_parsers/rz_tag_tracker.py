from typing import Union
from rottnest.gridsynth.gridsynth import DEFAULT_PRECISION

'''
    Adapter class for mapping Rz gates to tags 
'''

class RzTagTracker():

    '''
        Maps angles to tags
        TODO: This currently makes some very rough
        assumptions that no two gates will have
        the same angle and differing values of eps 
    '''
    def __init__(self, default_eps = None):
        # Reserve tag 0 
        self._angles_to_tags = {None: None}
        self._tags_to_angles = [None] 
        self._eps = [None] # Per tag eps 
        self.n_rz_gates = 0
    
        if default_eps is None:
            default_eps = DEFAULT_PRECISION + 3
    
        self.default_eps = default_eps

    def __getitem__(self, tag):
        return self._tags_to_angles[tag]

    def get_gridsynth_params(self, tag):
        '''
            Helper function to turn a tag into a gridsynth input
        '''
        if tag == 268435455:
            # Measurement gate tag
            angle = 0
            eps = 10
        else:
            angle = self._tags_to_angles[tag]
            eps = self._eps[tag]

        if eps is None: 
            eps = self.default_eps 

        return self.angle_to_rational(self, angle, precision=eps)


    def angle_to_rational(self, angle: float, *, precision: int = None, delta: int = 3) -> (int, int): 
        '''
            Converts an angle to a rational
        '''
        if precision is None:
            precision = self.default_eps 

        # In testing, increasing the precision by 2 ** 3 bounded the error on the conversion to rational   
        precision = precision + delta 

        denominator = int(2 ** eps) 
        numerator = int(angle * denominator)
        
        return numerator, denominator

    def trivial_angle_filters(self, numerator, denominator, eps) -> Union[tuple[int, int] | tuple[None, list]]:
        '''
            Skips trivial angles
        '''
        approx_angle = (numerator / denominator) % 2 
        if approx_angle < eps:
            return None, [] 

        if np.abs((approx_angle % 1) - 0.5) < eps:
            return None, ['S'] 

        if np.abs((approx_angle % 0.5) - 0.25) < eps:
            return None, ['T'] 

        return numerator, denominator

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
        return self.__repr__()

    def __repr__(self):
        return super().__repr__()
