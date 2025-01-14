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
    def __init__(self):
        self._angles_to_tags = dict()
        self._tags_to_angles = list()
        self._eps = list()

    def __getitem__(self, tag):
        return self._tags_to_angles[tag]

    def get(self, angle, eps): 
        '''
        Attempting to get a label is bound to allocating one
        '''
        tag = self._angles_to_tags.get(angle, None)
        if tag is None: 
            tag = len(self.angles_to_tags)
            self._angles_to_tags[angle] = tag 
            self._tags_to_angles.append(angle)
            self._eps.append(eps)
        return tag 

    def gets(self, *angles):
        return tuple(map(self.get, angles))

    def len(self):
        return len(self.labels)

    def __str__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()
