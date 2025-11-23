'''
    Tests for interface metaclassing
'''
import unittest

from rottnest.server.interface_spec.interface_spec import RouteInterfaceSpecification, ROTTNEST_PREFIX
from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.interface_spec import interface_exceptions


class NonResponder:
    '''
        Dummy class to not register or respond
    '''
    @classmethod
    def register(cls, *args, **kwargs):
        '''
        A non-register
        '''
        return lambda x: x

class InterfaceSpecTests(unittest.TestCase):
    '''
        Test the interface metaclassing
    '''

    def generate_specification(self, *routes):
        '''
            Factory method for specifications
        '''
        class TestSpec(RouteInterfaceSpecification):
            '''
                Specification factory template
            '''
        _routes = [f"{ROTTNEST_PREFIX}.{ROTTNEST_PREFIX}.{route}" for route in routes]

        TestSpec._routes = _routes
        return TestSpec


    def test_single_route(self):
        '''
            Test single correctly bound route
        '''
        spec = self.generate_specification('test')

        class TestInterface(RouteInterface):
            '''
                Test interface
            '''
            @RouteInterface.bind_route(ROTTNEST_PREFIX, 'test')
            @classmethod
            def test(cls, *args, **kwargs):
                '''
                    Dummy function
                '''

        interface = spec(NonResponder, TestInterface)
        assert len(interface.get_route_binds()) == 1

    def test_two_implementations(self):
        '''
            Test single correctly bound route
        '''
        spec = self.generate_specification('test', 'test_2')

        class TestInterface(RouteInterface):
            '''
                Test interface part 1
            '''
            @RouteInterface.bind_route(ROTTNEST_PREFIX, 'test')
            @classmethod
            def test(cls, *args, **kwargs):
                '''
                    Dummy function
                '''

        class TestInterface2(RouteInterface):
            '''
                Test interface part 2
            '''
            @RouteInterface.bind_route(ROTTNEST_PREFIX, 'test_2')
            @classmethod
            def test(cls, *args, **kwargs):
                '''
                    Dummy function
                '''

        interface = spec(NonResponder, TestInterface, TestInterface2)
        assert len(interface.get_route_binds()) == 2


    def test_no_routes(self):
        '''
            Test no routes case
        '''
        spec = self.generate_specification()
        try:
            interface = spec(NonResponder)
            # The above line should fail with a no routes exception
            assert False
        except interface_exceptions.NoRoutesException:
            pass

    def test_unbound_routes(self):
        '''
            Test unbound route
        '''
        spec = self.generate_specification('test')

        class TestInterface(RouteInterface):
            '''
                Empty class object
            '''

        try:
            interface = spec(NonResponder, TestInterface)
            # The above line should fail with a no routes exception
            assert False
        except interface_exceptions.MissingRouteException:
            pass

    def test_duplicate_routes(self):
        '''
            Test unbound route
        '''
        spec = self.generate_specification('test')

        try:
            class TestInterface(RouteInterface):
                '''
                    Test interface object
                '''

                @RouteInterface.bind_route(ROTTNEST_PREFIX, 'test')
                @classmethod
                def test(cls, *args, **kwargs):
                    '''
                        Dummy method
                    '''

                @RouteInterface.bind_route(ROTTNEST_PREFIX, 'test')
                @classmethod
                def test_2(cls, *args, **kwargs):
                    '''
                        Dummy method
                    '''

            interface = spec(NonResponder, TestInterface)
            # The above line should fail with a no routes exception
            assert False
        except interface_exceptions.DuplicateRouteException:
            pass


    def test_duplicate_routes_joint(self):
        '''
            Test for duplicate route registration
        '''
        spec = self.generate_specification('test')

        class TestInterface(RouteInterface):
            '''
                Object with test route bound
            '''
            @RouteInterface.bind_route(ROTTNEST_PREFIX, 'test')
            @classmethod
            def test(cls, *args, **kwargs):
                '''
                    Dummy method
                '''

        class TestInterface2(RouteInterface):
            '''
                Object with test route bound
            '''
            @RouteInterface.bind_route(ROTTNEST_PREFIX, 'test')
            @classmethod
            def test_2(cls, *args, **kwargs):
                '''
                    Dummy method
                '''

        try:
            interface = spec(NonResponder, TestInterface, TestInterface2)
            # The above line should fail with a no routes exception
            assert False
        except interface_exceptions.DuplicateRouteException:
            pass

    def test_additional_routes(self):
        '''
            Test for non-registered routes
        '''
        spec = self.generate_specification('test')

        class TestInterface(RouteInterface):
            '''
                Interface with an over-specification of routes
            '''
            @RouteInterface.bind_route(ROTTNEST_PREFIX, 'test')
            @classmethod
            def test(cls, *args, **kwargs):
                '''
                    Dummy method
                '''

            @RouteInterface.bind_route(ROTTNEST_PREFIX, 'test_2')
            @classmethod
            def test_2(cls, *args, **kwargs):
                '''
                    Dummy method
                '''

        try:
            interface = spec(NonResponder, TestInterface)
            # The above line should fail with a no routes exception
            assert False
        except interface_exceptions.UndefinedRouteException:
            pass

if __name__ == '__main__':
    unittest.main()
