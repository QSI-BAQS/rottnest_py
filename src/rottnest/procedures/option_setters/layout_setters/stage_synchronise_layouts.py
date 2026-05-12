'''
    Stage for setting layouts
'''
from rottnest.procedures import stage
from rottnest.compute_units.layout_proxy import LayoutProxy

STAGE_TAG = 'synchronise_layouts'

class SynchroniseLayoutsStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, layouts: dict, *, tag=None, dependencies=None):
        '''
            Takes a dicitionary with keys as layout ids and values
             as layouts
        '''
        self._complete = False
        self._layouts = layouts

        if dependencies is None:
            dependencies = []

        super().__init__(
            tag=tag,
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, compiler_environment):
        '''
            Swaps the current rottnest architecture
        '''
        # This bound is reasonably performant
        for layout_id, layout_json in self._layouts:
            LayoutProxy.add_layout_with_id(
                layout_id, layout_json
            )

        self._complete = True
