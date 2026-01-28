from rottnest.compilation_procedures import stage

PANDORA_LOAD_TAG = 'Pandora Load'

class PandoraLoadStage(stage.RottnestCompilerStage):
    TAG = PANDORA_LOAD_TAG

    def __init__(self):
        super().__init__()

    def execute(self, environment):
        # TODO
        pass
