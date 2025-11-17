import unittest

from rottnest.server.interface_spec.interface_spec import RouteInterfaceSpecification
from rottnest.server.interface_spec.route_interface import RouteInterface 

from rottnest.server.interface_spec import interface_exceptions 


class NonResponder:
    '''
        Dummy class to not register or respond 
        Assertion logic is in the specification constructor
    '''
    @classmethod
    def register(cls, *args, **kwargs):
        '''
        A non-register
        '''
        return lambda x: x 


class ControllerRouteTests(unittest.TestCase):

    @staticmethod
    def assert_binds(spec, interface):
        '''
            Runs the constructor of the specification using the interface 
            Assertion statements are in the constructor
        '''
        interface = spec(NonResponder, interface) 

    def test_callgraph(self):
        '''
            Tests callgraph endpoints
        '''
        from rottnest.server.interface_spec.specs.callgraph_spec import CallGraphSpecification as spec
        from rottnest.server.controller.callgraph import CallGraphInterface as interface
        self.assert_binds(spec, interface)

    def test_architecture(self):
        '''
        Tests architecture endpoints
        '''
        from rottnest.server.interface_spec.specs.architecture_spec import ArchitectureSpecification  as spec
        from rottnest.server.controller.architecture import ArchitectureInterface as interface
        self.assert_binds(spec, interface)

    def test_executables(self):
        '''
        Tests executable endpoints
        '''
        from rottnest.server.interface_spec.specs.executable_spec import ExecutableSpecification  as spec
        from rottnest.server.controller.executable import ExecutableInterface as interface
        self.assert_binds(spec, interface)

    def test_layouts(self):
        '''
        Tests layout endpoints
        '''
        from rottnest.server.interface_spec.specs.layout_spec import LayoutSpecification  as spec
        from rottnest.server.controller.layout import LayoutInterface as interface
        self.assert_binds(spec, interface)
   
if __name__ == '__main__':
    c = ControllerRouteTests()
    c.test_callgraph()
    c.test_architecture()
    c.test_executables()
    c.test_layouts()
