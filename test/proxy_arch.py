from rottnest.compute_units.architecture_proxy import ArchitectureProxy, saved_architectures

def arch_factory(n_qubits, arch_id):
    '''
        Factory
    '''

    class ProxyArch(ArchitectureProxy):
        def __new__(cls): 
            return object.__new__(ProxyArch)

        def check_pregenerated(self):
            return True

        def __init__(self, *args, **kwargs): 
            pass

        def mem_bound(self):
            return n_qubits 
        
        def underlying_json(self):
            return ""

    saved_architectures[arch_id] = object()
    arch = ProxyArch()
    saved_architectures[arch_id] = arch 
    return arch

