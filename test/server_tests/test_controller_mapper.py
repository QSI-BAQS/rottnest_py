
import unittest
import json

from rottnest.server.controller_mapper import ControllerMapper
from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.controller.architecture import ArchitectureInterface
from rottnest.server.controller.executable import ExecutableInterface
from rottnest.server.controller.layout import LayoutInterface
from rottnest.server.controller.callgraph import CallGraphInterface


class DummyInterface(RouteInterface):

    @RouteInterface.bind_route("dummyiface", 'get_dummy')
    @classmethod
    def get_dummy(cls, message, **kwargs):
        '''
           Dummy method that will return a dict 
        '''
        return {
            'property': 'value',
            'easily': 'serialisable'
        }
        
        
class ControllerMapperTests(unittest.TestCase):
    '''
       When constructing the controller mapper, we should
       observe that the mapper is able to have constructed functions that
       it can use
    '''

    ENDPOINTS = {
        "architecture": ([
            ('arch.get_list', { 'payload': '' }),
            ('arch.get_current', { 'payload': '' }),
            ('arch.set_current', {'payload': '' }),
            ('arch.set_config', {'payload': '' }),
            ('arch.get_config', {'payload': '' }),
        ], ArchitectureInterface),
        "executable": ([
            ('executable.get_list', { 'payload': '' }),
            ('executable.get_current', { 'payload': '' }),
            ('executable.set_current', {'payload': '' }),
            ('executable.set_config', {'payload': '' }),
            ('execubtable.get_config', {'payload': '' }),
        ], ExecutableInterface),
        "callgraph": ([
            ('callgraph.get_root_graph', { 'payload': '' }),
            ('callgraph.get_graph', { 'payload': '' }),
            ('callgraph.get_status', {'payload': '' }),
            ('callgraph.un_graph_node', {'payload': '' }),
        ], CallGraphInterface),
        "layout": ([
            ('layout.run_layout', { 'payload': '' }),
            ('layoutset_layout', { 'payload': '' }),
        ], LayoutInterface)
    }

    @staticmethod
    def err_fn():
        '''
           Error function - Will failure/return false 
        '''
        return False

    @staticmethod
    def endpoint_check(endpoints, cls_obj_list):

        
        prefix = 'rottnest'
        controller_mapper_builder = ControllerMapper.assemble()

        for clobj in cls_obj_list:
            controller_mapper_builder.attach(clobj)

        controller_mapper_obj = controller_mapper_builder.build()
        
        for etup in endpoints:
            (endpoint, payload) = etup
            route_fullname = '{}.{}'.format(prefix, endpoint)
            message = { 'message': route_fullname, "payload": payload }
            mapper_fn = controller_mapper_obj.get(message['message'],
                                              ControllerMapperTests.err_fn)
            # NOTE: Will reserve this for other test objects
            # mapobj = mapper_fn(ArchitectureInterface, message)

            assert mapper_fn is not None
            assert hasattr(mapper_fn, '__call__')

    def test_simple_mapper_construction(self):
        '''
          Simple construction with a dummy interface that
          contains at least one endpoint  
        '''
        controller_mapper_obj = ControllerMapper.assemble() \
            .attach(DummyInterface) \
            .build()

        assert controller_mapper_obj is not None
        assert controller_mapper_obj.get('rottnest.dummyiface.get_dummy',
                                     ControllerMapperTests.err_fn) is not None        
        

    def test_mapper_serialisation(self):
        '''
           Given a simple construction and dummy interface,
           the mapper should return an expected object that is serialisable 
        '''
        
        controller_mapper_obj = ControllerMapper.assemble() \
            .attach(DummyInterface) \
            .build()

        mapper_fn = controller_mapper_obj.get('rottnest.dummyiface.get_dummy',
                                          ControllerMapperTests.err_fn)
        mapobj = mapper_fn(None, {'data': 'nothing data'})
        

        assert hasattr(mapper_fn, '__call__')
        assert mapobj is not None
        assert isinstance(mapobj, str)

        deserialised = json.loads(mapobj)

        assert deserialised is not None
        assert isinstance(deserialised, dict)
        

    def test_mapper_with_architecture_interface(self):
        '''
           Given a mapper and architecture interface, we should be able to
           construct it with this existing interface 
        '''

        endpoints = ControllerMapperTests.ENDPOINTS['architecture'][0]

        ControllerMapperTests.endpoint_check(endpoints,
                                             [ArchitectureInterface])



    def test_mapper_with_executable_interface(self):
        '''
           Given a mapper and executable interface we should be able to
           construct it with this existing interface 
        '''

        endpoints = ControllerMapperTests.ENDPOINTS['executable'][0]

        ControllerMapperTests.endpoint_check(endpoints,
                                             [ExecutableInterface])

    def test_mapper_with_callgraph_interface(self):
        '''
           Given a mapper and callgraph interface, we should be able to construct it
           with this existing interface 
        '''
        endpoints = ControllerMapperTests.ENDPOINTS['callgraph'][0]

        ControllerMapperTests.endpoint_check(endpoints,
                                             [CallGraphInterface])


    def test_mapper_with_layouts_interface(self):
        '''
           Given a mapper and layouts interface, we should be able to construct it with this existing interface 
        '''
        endpoints = ControllerMapperTests.ENDPOINTS['layout'][0]

        ControllerMapperTests.endpoint_check(endpoints,
                                             [LayoutInterface])



    def test_mapper_with_all_interfaces(self):
        '''
           Given the interfaces, it will test and combine all the interfaces itno the same mapper
           and test them 
        '''
        endpoints = []
        interfaces = []
        for k, e in ControllerMapperTests.ENDPOINTS.items():
            interface_endpoints = e[0]
            class_obj = e[1]    
            endpoints.extend(interface_endpoints)

            interfaces.append(class_obj)
            

        ControllerMapperTests.endpoint_check(endpoints, interfaces)
