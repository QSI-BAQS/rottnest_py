from rottnest.monkey_patchers import pyliqtr_patcher
from rottnest.pandora.pandora_cache import pandora_cache 

from rottnest.executables.executable import RottnestExecutable

from pyLIQTR.utils.circuit_decomposition import circuit_decompose_multi

class T_RZ_RottnestExecutable(RottnestExecutable):
    '''
        Naive executable with all bounds replaced by counting methods 
        Useful for smaller circuits, but will not scale well
    '''

    _n_rz = None
    _n_T = None
    _cache_layer = 1

    def n_T(self) -> int:
        '''
            Calculate number of Rz gates required
            Naively assume that these are all
            T gates
        '''
        if self._n_T is None:
            qc = self._generate_circuit()
            self._n_rz = self.count_rz_cirq(qc)
        return self._n_rz 
        


    def n_rz(self) -> int:
        '''
            Calculate number of rz gates required
        '''
        if self._n_rz is None:
            qc = self._generate_circuit()
            self._n_rz = self.count_rz_cirq(qc)
        return self._n_rz 


    def precompute(self):
        '''
            Collects all hashed operations and injects them into Pandora
        '''
        if self.pandora:
            circuit = self._generate_circuit()
            for layer in circuit_decompose_multi(circuit, self._cache_layer):
                for op in layer:
                    if type(op.gate) in pyliqtr_patcher.hash_function_patchers: 
                        
                        if not pandora_cache.in_cache(op):
                            hsh = op._rottnest_hash()
                            pandora_cache.bind_hash(op) 
