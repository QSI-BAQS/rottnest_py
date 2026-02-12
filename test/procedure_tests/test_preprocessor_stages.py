import unittest

from rottnest.procedures.preprocessor import stage_pandora_store
from rottnest.procedures import stage

 
class PreprocessorStageTest(unittest.TestCase):

    def test_stage_pandora_tag(self):

        pandora_stage = stage_pandora_store.PandoraLoadStage() 
        assert pandora_stage.get_tag() == stage_pandora_store.STAGE_TAG 




if __name__ == '__main__':
    tst = CompilerStageTest()
    tst.test_stage_default_tag()

    #unittest.main()
