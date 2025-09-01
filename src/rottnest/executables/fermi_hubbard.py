from rottnest.executables.t_rz_executable import T_RZ_RottnestExecutable

from rottnest.executables import fermi_hubbard_rigetti 


class FermiHubbard(T_RZ_RottnestExecutable):
    '''
        Fermi Hubbard Model
    '''

    DEFAULT_N = 5
    DEFAULT_p_algo = 0.95
    DEFAULT_times = 1.0

    @staticmethod
    def get_parameters():
        '''
            Returns the parameters of the executable 
            This can then be passed to the front-end
        '''
        return {
                'N':(int, FermiHubbard.DEFAULT_N),
                'p_algo':(float, FermiHubbard.DEFAULT_p_algo),
                'times':(float, FermiHubbard.DEFAULT_times)
        }

    def _generate_circuit(self):
        '''
            Dispatch via interface
        '''
        return self._make_fh_circuit()

# License separation 
FermiHubbard._make_fh_circuit = fermi_hubbard_rigetti.make_fh_circuit
FermiHubbard._make_qsvt_circuit = fermi_hubbard_rigetti.make_qsvt_circuit
