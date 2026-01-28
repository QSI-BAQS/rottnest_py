import unittest

from rottnest.compilation_procedures import procedure, stage 
class CompilerStageTest(unittest.TestCase):

    def test_stage_constructor_tag(self):

        class A(stage.RottnestCompilerStage):
            def __init__(self, tag = None):
                super().__init__(tag=tag)

            def execute(self, obj):
                ...
      
        tag = 'tag' 
        a = A(tag=tag)  
        assert stage.stage_tag(a) == tag

    def test_stage_default_tag(self):

        class A(stage.RottnestCompilerStage):
            def __init__(self, tag=None):
                super().__init__(tag=tag)

            def execute(self, obj):
                ...
      
        a = A()  
        assert stage.stage_tag(a) == stage.stage_tag(A) 





if __name__ == '__main__':
    tst = CompilerStageTest()
    tst.test_stage_default_tag()

    #unittest.main()
