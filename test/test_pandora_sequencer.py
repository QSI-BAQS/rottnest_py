#from pandora.pandora import Pandora

from rottnest.compute_units.architecture_proxy import ArchitectureProxy, saved_architectures


from rottnest.pandora.pandora_sequencer import PandoraSequencer 

#pan.build_pandora()

# Todo argv this
not_widgetized = False
if not_widgetized:
    pan.build_pandora()
    pan.build(...)   # Object to build
    pan.build_edge_list()


def arch_constructor(n_qubits):
    class ProxyArch(ArchitectureProxy):
        def __new__(cls): 
            return object.__new__(ProxyArch)

        def check_pregenerated(self):
            return True

        def __init__(self, *args, **kwargs): 
            pass

        def num_qubits(self):
            return n_qubits 
        
        def underlying_json(self):
            return ""

    saved_architectures[666] = object()
    saved_architectures[666] = ProxyArch() 
    return 666 



arch = arch_constructor(100) 
seq = PandoraSequencer(arch)

for compute_unit in seq.sequence_pandora():
    print(compute_unit)
