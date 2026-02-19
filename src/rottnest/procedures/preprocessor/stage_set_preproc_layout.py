'''
    Stage for hotswapping architectures
'''
from rottnest.procedures import stage
from rottnest.compute_units.layout_proxy import LayoutProxy

from . import stage_set_preproc_architecture

STAGE_TAG = 'hotswap_layout'

class SetPreprocessingLayoutStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        self._complete = False

        self._backup = None
        dependencies = [
            stage_set_preproc_architecture.STAGE_TAG
        ]
 
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, compiler_environment):
        '''
            Swaps the current rottnest architecture 
        '''
        # Todo replace with dynamic string
        self._backup = LayoutProxy.flush() 

        # This bound is reasonably performant
        layout_id = 0
        memory_bound = 1000
        layout = {'mem_bound': memory_bound}
        LayoutProxy.add_layout_with_id(layout_id, layout)

        self._complete = True

    def get_original_layout(self):
        '''
            Getter for the hotswapped architecture
        '''
        return self._backup
