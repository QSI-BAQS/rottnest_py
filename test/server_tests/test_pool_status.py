'''
    Tests for the status update decorator
'''
import unittest

from rottnest.process_pool.status_decorator import status_update
from rottnest.process_pool.pool_status import PoolStatus

class StatusDecoratorTests(unittest.TestCase):
    '''
        Tests for the status update decorator
    '''

    class STATUS_DECORATOR_TEST_EXCEPTION(Exception):
        '''
            Exception class for hooking mid-test calls
        '''

    def gen_class(self, decorator):
        '''
            Class factory with decorator hook
        '''
        class StatusHolder:
            '''
                Duck-typed status proxy
            '''
            def __init__(self):
                '''
                    Constructor
                '''
                self._status = PoolStatus.UNSTARTED

            def set_status(self, status):
                '''
                    Setter
                '''
                self._status = status

            def get_status(self):
                '''
                    Getter
                '''
                return self._status

            @decorator
            def hooked(self, *args, interrupt=False, **kwargs):
                '''
                    Hooking function
                '''
                if interrupt:
                    raise StatusDecoratorTests.STATUS_DECORATOR_TEST_EXCEPTION
        return StatusHolder

    def test_prior(self):
        '''
            Test prior to hook
        '''

        def null_decorator(fn):
            return fn

        cls = self.gen_class(null_decorator)
        obj = cls()
        assert obj.get_status() is PoolStatus.UNSTARTED

        obj.hooked()
        assert obj.get_status() is PoolStatus.UNSTARTED

    def test_post(self):
        '''
            Test status after the function has completed
        '''
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
        '''
            Test during hooked function execution
        '''

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
