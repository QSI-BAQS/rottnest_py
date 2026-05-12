'''
    Stage for setting layouts
'''
from rottnest.procedures import stage
from rottnest.compute_units.layout_proxy import LayoutProxy

STAGE_TAG = 'set_layout'

class SetLayoutStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, layout, *, tag=None, dependencies=None):
        self._complete = False
        self._layout = layout

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
        layout_id = 0
        LayoutProxy.add_layout_with_id(layout_id, self._layout)

        self._complete = True
