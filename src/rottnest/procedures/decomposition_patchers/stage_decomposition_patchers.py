from rottnest.procedures import stage

from rottnest.plugins import executables
from rottnest.monkey_patchers import add_pyliqtr_hash, add_qualtran_hash, add_cirq_hash, load_hash_patcher


STAGE_TAG = 'Pyliqtr_Patches'

class DecomposerPatchStage(stage.RottnestCompilerStage):
    '''
        Loads hash functions from the executable
        and patches them into the decomposer 
    '''
    TAG = STAGE_TAG 

    def __init__(self):
        super().__init__()

    def execute(self, environment):
        '''
            Loads the appropriate patchers from the executable
            And passes them to the monkey patcher
        '''
        executable = executables.get_current_executable()

        for patcher, fn in executable.pyliqtr_patchers().items():
            add_pyliqtr_hash(patcher, fn)

        for patcher, fn in executable.qualtran_patchers().items():
            add_qualtran_hash(patcher, fn)

        for patcher, fn in executable.cirq_patchers().items():
            add_cirq_hash(patcher, fn)

        # executable.cirq_gate_decomposers()

        # Trigger a reload of the monkey patchers
        load_hash_patcher()
