'''
    Tests for the status update decorator
'''
import unittest
from functools import partial

from rottnest.server.model.process_pool import status_update, PoolStatus 

class StatusDecoratorTests(unittest.TestCase):

    class STATUS_DECORATOR_TEST_EXCEPTION(Exception):
        ...

    def gen_class(self, decorator):

        class StatusHolder:
            def __init__(self):
                self._status = PoolStatus.UNSTARTED 
            def set_status(self, status):
                self._status = status

            def get_status(self):
                return self._status

            @decorator
            def hooked(self, *args, interrupt=False, **kwargs):
                if interrupt:
                    raise StatusDecoratorTests.STATUS_DECORATOR_TEST_EXCEPTION 
        
        return StatusHolder

    def test_prior(self):
        def null_decorator(fn): 
            return fn

        cls = self.gen_class(null_decorator) 
        obj = cls()
        assert obj.get_status() is PoolStatus.UNSTARTED

        obj.hooked()
        assert obj.get_status() is PoolStatus.UNSTARTED
    
    def test_post(self):
        cls = self.gen_class(
            status_update( 
                PoolStatus.STARTING,
                PoolStatus.IDLE
            )
        )
        obj = cls()
        assert obj.get_status() is PoolStatus.UNSTARTED

        obj.hooked()
        assert obj.get_status() is PoolStatus.IDLE


    def test_during(self):
        cls = self.gen_class(
            status_update( 
                PoolStatus.STARTING,
                PoolStatus.IDLE
            )
        )
        obj = cls()
        assert obj.get_status() is PoolStatus.UNSTARTED

        try:
            obj.hooked(interrupt=True)
            assert False
        except StatusDecoratorTests.STATUS_DECORATOR_TEST_EXCEPTION:
            pass 

        assert obj.get_status() is PoolStatus.STARTING



if __name__ == '__main__':
    unittest.main()
