'''
    Qubit Label Tracker
    Adapter class for mapping qubits to indices  
'''

class RegisterContext:
    '''
        Context tracker class
        Detects if a qubit is in context or not, 
        and by extension is used to track non-participatory qubits 
    '''
    def __init__(self, context=None, global_context = None):
        if context is None:
            context = set()
        self._context = context
        self._global_context = global_context 

    def __iter__(self):
        return self._context.__iter__()

    def __in__(self, label):
        '''
            Checks if an item is in context
        '''
        return label in self._context 

    def get(self, label): 
        pass

    def copy(self):
        '''
            Triggers a copy of the context
        '''
        return set(self._context)

class QubitLabelTracker:
    '''
        Tracks Qubit Labels
        Dictionary acting over hashable objects
        The get methods acts to retrieve a qubit label
            if one has been allocated for that object 
        The __getitem__ method retrieves the original object
            given a qubit label

        Acts an adapter
    '''
    def __init__(self, context: RegisterContext = None, global_context: RegisterContext = None):
        self._labels = dict()
        self._local_labels = dict()
        if context is None:
            context = RegisterContext(global_context=global_context) 
        self._context = context
        self._global_context = global_context
        self.n_inputs = 0 

    def __getitem__(self, qubit_label):
        return self.get(qubit_label)

    def get(self, qubit_label): 
        '''
        Attempting to get a label 
        '''
        index = self._labels.get(qubit_label, None)

        # Qubit has not yet been encountered
        if index is None: 
            # Index was teleported from the context
            # Increase Bell state overhead
            if index in self._context:
                n_inputs += 1
            index = len(self._labels)
            self._labels[qubit_label] = index
        return index

    def gets(self, *labels):
        return tuple(map(self.get, labels))

    def __len__(self):
        return len(self._labels)

    def __str__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()
