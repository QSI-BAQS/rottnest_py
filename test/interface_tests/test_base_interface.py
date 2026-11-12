'''
    Tests the base Interface specification
'''

import unittest
from rottnest.utils.interface import Interface, interface, interface_argcount, interface_argfilter, InterfaceSpecificationError, InterfaceFilterError

class BaseInterfaceTests(unittest.TestCase):
    '''
        Test the base interface specification
    '''

    def test_registration(self):
        '''
            Checks that classes are being
            correctly registered
        '''
        obj = type('Name', tuple(), {})

        interface(obj)
        assert obj in Interface._INTERFACES

    def test_decorator_registration(self):
        '''
            Checks that decorator based registration is functioning as expected
        '''
        @interface
        class A:
            pass
        assert A in Interface._INTERFACES

    def test_argcount_registration(self):
        '''
            check that the argcounts are being registered
        '''
        @interface
        class A:
            @interface_argcount
            def foo(self, x):
                pass

        obj = Interface._INTERFACES.get(A, None)
        assert obj is not None
        assert len(obj.collected_argcount) == 1

    def test_argcount_validation_matching(self):
        '''
            Checks that a matching case does not throw an error 
        '''

        @interface
        class A:
            @interface_argcount
            def foo(self, x):
                pass

        class B(A):
            def foo(self, y):
                pass

        Interface.validate_interface_implementation(B)

    def test_argcount_validation_not_matching(self):
        '''
            Checks that a matching case does not throw an error 
        '''

        @interface
        class A:
            @interface_argcount
            def foo(self, x):
                pass

        try:
            # This should throw an exception on instantiation
            class B(A):
                def foo(self, y, z):
                    pass
            assert False
        except InterfaceSpecificationError:
            pass
        

    def test_argfilter_validation_matching(self):
        '''
            Checks that a matching case does not throw an error 
        '''

        @interface
        class A:
            @interface_argfilter(lambda base, instance: True)
            def foo(self, x):
                pass

        class B(A):
            def foo(self, y, z):
                pass

    def test_argfilter_validation_not_matching(self):
        '''
            Checks that a matching case does not throw an error 
        '''

        @interface
        class A:
            @interface_argfilter(lambda base, instance: False)
            def foo(self, x):
                pass

        try:
            # This should throw an exception on instantiation
            class B(A):
                def foo(self, y, z):
                    pass
            assert False

        except InterfaceFilterError:
            pass
            


if __name__ == '__main__':
    tst = BaseInterfaceTests()

    tst.test_argcount_validation_not_matching()
    tst.test_argcount_validation_matching()

    #unittest.main()
