import unittest

from rottnest.server.interface_spec.interface_spec import RouteInterfaceSpecification
from rottnest.server.interface_spec.route_interface import RouteInterface 

from rottnest.server.interface_spec import interface_exceptions 


class InterfaceSpecTests(unittest.TestCase):
    '''
        Test the interface metaclassing
    '''

    def generate_specification(self, *routes):
        class TestSpec(RouteInterfaceSpecification):
            ...
        TestSpec._routes = routes
        return TestSpec


    def test_single_route(self):    
        '''
            Test single correctly bound route
        ''' 
        spec = self.generate_specification('test')
 
        class TestInterface(RouteInterface): 

            @RouteInterface.bind_route('test')
            @classmethod
            def test(cls, *args, **kwargs):
                    ...
        interface = spec(None, TestInterface)
        assert len(interface.get_route_binds()) == 1

    def test_two_implementations(self):    
        '''
            Test single correctly bound route
        ''' 
        spec = self.generate_specification('test', 'test_2')
 
        class TestInterface(RouteInterface): 

            @RouteInterface.bind_route('test')
            @classmethod
            def test(cls, *args, **kwargs):
                    ...

        class TestInterface2(RouteInterface): 

            @RouteInterface.bind_route('test_2')
            @classmethod
            def test(cls, *args, **kwargs):
                    ...

        interface = spec(None, TestInterface, TestInterface2)
        assert len(interface.get_route_binds()) == 2


    def test_no_routes(self):
        '''
            Test no routes case
        '''
        spec = self.generate_specification()
        try:
            interface = spec(None)
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
            pass


        try:
            interface = spec(None, TestInterface)
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
                @RouteInterface.bind_route('test')
                @classmethod
                def test(cls, *args, **kwargs):
                        ...
                @RouteInterface.bind_route('test')
                @classmethod
                def test_2(cls, *args, **kwargs):
                        ...


            interface = spec(None, TestInterface)
            # The above line should fail with a no routes exception
            assert False
        except interface_exceptions.DuplicateRouteException:
           pass 
            

    def test_duplicate_routes_joint(self):
        spec = self.generate_specification('test')

        class TestInterface(RouteInterface): 
            @RouteInterface.bind_route('test')
            @classmethod
            def test(cls, *args, **kwargs):
                ...

        class TestInterface2(RouteInterface): 

            @RouteInterface.bind_route('test')
            @classmethod
            def test_2(cls, *args, **kwargs):
                    ...

        try:
            interface = spec(None, TestInterface, TestInterface2)
            # The above line should fail with a no routes exception
            assert False
        except interface_exceptions.DuplicateRouteException:
           pass 

    def test_additional_routes(self): 
        spec = self.generate_specification('test')

        class TestInterface(RouteInterface): 
            @RouteInterface.bind_route('test')
            @classmethod
            def test(cls, *args, **kwargs):
                ...

            @RouteInterface.bind_route('test_2')
            @classmethod
            def test_2(cls, *args, **kwargs):
                ...

        try:
            interface = spec(None, TestInterface)
            # The above line should fail with a no routes exception
            assert False
        except interface_exceptions.UndefinedRouteException:
            pass
     
