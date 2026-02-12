from rottnest.compilation_procedures import stage

STAGE_TAG = 'Pandora Load'

class PandoraLoadStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG 

    def __init__(self):
        super().__init__()

    def execute(self, environment):
        # TODO
        pass
