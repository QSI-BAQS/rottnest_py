'''
    Derived class from RottnestExecutable for T Rz based compilation
'''

# from rottnest.pandora.pandora_cache import pandora_cache
from rottnest.executables.executable import RottnestExecutable


class T_RZ_RottnestExecutable(RottnestExecutable):
    '''
        Naive executable with all bounds replaced by counting methods
        Useful for smaller circuits, but will not scale well
    '''

    _n_rz: int | None = None
    _n_T: int | None = None
    _cache_layer = 1

    def n_T(self) -> int:
        '''
            Calculate number of Rz gates required
            Naively assume that these are all
            T gates
        '''

    def n_rz(self) -> int:
        '''
            Calculate number of rz gates required
        '''

    def precompute(self, *_args, **_kwargs):
        '''
            Collects all hashed operations and injects them into Pandora

        if self._pandora:
            circuit = self._generate_circuit()
            for layer in circuit_decompose_multi(circuit, self._cache_layer):
                for op in layer:
                    if type(op.gate) in pyliqtr_patcher.hash_function_patchers:
                        if not pandora_cache.in_cache(op):
                            _hsh = op._rottnest_hash()
                            # NOTE: This apparently
                            pandora_cache.bind_hash(op)
        '''
