import unittest

from rottnest.procedures import procedure, stage 
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



    def test_asynch(self):
        class AsynchStage(stage.RottnestCompilerStage):
            def __init__(self, tag=None, dependencies=None):
                self._complete = False
                super().__init__(
                    tag=tag,
                    dependencies=dependencies,
                    asynchronous=True
                )

            def poll(self, obj):
                self._complete = True

            def execute(self, obj):
                return False

            def complete(self):
                return self._complete

        obj = AsynchStage() 
        assert obj.execute(object()) is False
        assert obj.is_asynchronous() is True
        assert obj.complete() is False

        obj.poll(object())
        assert obj.complete() is True 


if __name__ == '__main__':
    tst = CompilerStageTest()
    tst.test_stage_default_tag()

    #unittest.main()
