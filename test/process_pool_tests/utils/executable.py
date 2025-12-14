from rottnest.executables.executable import RottnestExecutable


class CirqExecutable(RottnestExecutable):
    '''
        Sample wrapper on cirq objects
        Performs no caching, used for testing only
    '''
    def __init__(self, obj):
        self._cirq_obj = obj

    @staticmethod
    def get_parameters():
        '''
            No parameters
        '''
        return {}

    def _generate_circuit(self):
        return self._cirq_obj

    def prec_rz(self):
        return 10
