import unittest

from rottnest.procedures import preprocessor
from rottnest.procedures import stage

from rottnest.plugins import architectures
 
class PreprocessorStageTest(unittest.TestCase):

    def test_stage_pandora_tag(self):

        pandora_stage = preprocessor.stage_pandora_store.PandoraLoadStage() 
        assert pandora_stage.get_tag() == preprocessor.stage_pandora_store.STAGE_TAG 


    def test_stage_hotswap(self):
        swap_arch = preprocessor.stage_set_preproc_architecture.SetPreprocessingArchitectureStage()
        swap_arch.execute(None)
        assert architectures.get_current_architecture().get_name() == 'Rz Counter' 


    def test_stage_reset(self):
        swap_arch = preprocessor.stage_set_preproc_architecture.SetPreprocessingArchitectureStage()
        swap_arch.execute(None)
        assert architectures.get_current_architecture().get_name() == 'Rz Counter' 
        arch = architectures.get_current_architecture() 

        class Obj:
           hotswap_architecture = swap_arch 


        reset_arch = preprocessor.stage_reset_preproc_architecture.ResetPreprocessingArchitectureStage() 
        reset_arch.execute(Obj)
        print("TST")
        print("Arch:", architectures.get_current_architecture())
#        assert architectures.get_current_architecture() is None



if __name__ == '__main__':
    tst = PreprocessorStageTest()
    tst.test_stage_reset()

    #unittest.main()
