from rottnest.executables.executable import RottnestExecutable

from rottnest.executables import fermi_hubbard_rigetti 

class FermiHubbard(RottnestExecutable):
    '''
        Fermi Hubbard Model
    '''
    def __init__(self,
        N=5,
        p_algo=0.95,
        times=1.0
        ):
        '''
            Constructor
        '''
        
        self.N = N
        self.p_algo = p_algo
        self.times = times
                 
        self.precompute()

    @staticmethod
    def get_parameters():
        '''
            Returns the parameters of the executable 
            This can then be passed to the front-end
        '''
        return {'N':int, 'p_algo':float, 'times':float}

    def precompute(self):
        pass
 
    def _generate_circuit(self):
        '''
            Dispatch via interface
        '''
        return self._make_fh_circuit()

# License separation 
FermiHubbard._make_fh_circuit = fermi_hubbard_rigetti.make_fh_circuit
FermiHubbard._make_qsvt_circuit = fermi_hubbard_rigetti.make_qsvt_circuit
