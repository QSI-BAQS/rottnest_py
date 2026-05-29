import unittest

from rottnest.process_pool.single_instantiation import (
    SingleInstantiation,
    InstantiatingBlockedObjectException, 
    BlockingInstantiatedObjectException,
    MultipleInstantiationException,
    NotSingleInstantiationSubclassException,
    block_instantiation)

class TestSingleInstantiation(unittest.TestCase):

    def class_builder(self):
        '''
            Builds dummy classes for testing
        '''

        class Obj(SingleInstantiation):
            def __init__(self):
                ...
        return Obj

    def test_single_init(self):
        '''
            Tests that only one init may occur
        '''
        Obj = self.class_builder()
        
        a = Obj()
         
        # Second init should fail
        try:
            _ = Obj()
            # Should not reach
            assert False
        except MultipleInstantiationException:
            pass

    def test_class_scoping(self):
        '''
            Ensuring that the single init restriction is
            correctly per-class
        '''
        Obj_a = self.class_builder()
        Obj_b = self.class_builder()
        Obj_c = self.class_builder()

        # Compared to the previous test, none of these
        # should fail
        a = Obj_a()
        b = Obj_b()
        c = Obj_c()

        # Second init should fail for each
        for Obj in [Obj_a, Obj_b, Obj_c]:
            try:
                _ = Obj()
                # Should not reach
                assert False
            except MultipleInstantiationException:
                pass

    def test_block_then_init(self):
        Obj = self.class_builder()
        
        SingleInstantiation.block_instantiation(Obj)
 
        # Init should fail
        try:
            a = Obj()
            # Should not reach
            assert False
        except InstantiatingBlockedObjectException:
            pass

    def test_init_then_block(self):
        Obj = self.class_builder()
        
        a = Obj()
 
        # Init should fail
        try:
            SingleInstantiation.block_instantiation(Obj)
            # Should not reach
            assert False
        except BlockingInstantiatedObjectException:
            pass

    def test_dispatch_init_then_block(self):
        '''
            Checks the dispatch function rather than the base function
        '''
        Obj = self.class_builder()
        
        a = Obj()
 
        # Init should fail
        try:
            block_instantiation(Obj)
            # Should not reach
            assert False
        except BlockingInstantiatedObjectException:
            pass

    def test_dispatch_block_then_init(self):
        Obj = self.class_builder()
        
        block_instantiation(Obj)
 
        # Init should fail
        try:
            a = Obj()
            # Should not reach
            assert False
        except InstantiatingBlockedObjectException:
            pass

    def test_block_non_inheriting(self):
        '''
            Test that blocks can't be called on
            objects that don't inherit from 
            SingleInstantiation
        '''
        Obj = object
       
        try: 
            block_instantiation(Obj)
            assert False 
        except NotSingleInstantiationSubclassException:
            pass




if __name__ == '__main__':
    unittest.main()
