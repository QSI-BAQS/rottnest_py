'''
    Stage for hotswapping architectures
'''
from rottnest.plugins import architectures, executables
from rottnest.procedures import stage


from rottnest.procedures.pool import procedure_pool
from rottnest.compute_units.layout_proxy import LayoutProxy

from . import stage_set_preproc_layout
from . import stage_reset_preproc_architecture


STAGE_TAG = 'reset_layout'

class ResetPreprocessingLayoutStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        self._complete = False

        if dependencies is None:
            dependencies = [
                stage_set_preproc_layout.STAGE_TAG,
                stage_reset_preproc_architecture.STAGE_TAG,
                procedure_pool.STAGE_TAG
            ] 

        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, environment):
        '''
            Resets a swapped layouts back to the
            original ones
        '''
        layouts = environment.hotswap_layout.get_original_layout()
        LayoutProxy.reload_layouts(layouts) 
        self._complete = True
