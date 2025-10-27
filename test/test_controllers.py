import unittest

from rottnest.server.interface_spec.interface_spec import RouteInterfaceSpecification
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


class ControllerRouteTests(unittest.TestCase):

    def test_callgraph(self):
        '''
            Tests callgraph endpoints
        '''
        from rottnest.server.interface_spec.specs.callgraph_spec import CallGraphSpecification  
        from rottnest.server.controller.callgraph import CallGraphInterface
    
        spec = CallGraphSpecification
        interface = spec(NonResponder, CallGraphInterface) 

    def test_architecture(self):
        '''
        Tests architecture endpoints
        '''
        from rottnest.server.interface_spec.specs.architecture_spec import ArchitectureSpecification  
        from rottnest.server.controller.architecture import ArchitectureInterface
    
        spec = ArchitectureSpecification
        interface = spec(NonResponder, ArchitectureInterface) 
