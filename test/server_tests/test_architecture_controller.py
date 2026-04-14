'''
   Tests for the architecture controller, ensuring
   it meets particular criteria 
'''
import json
import unittest
from rottnest.server.controller.architecture import ArchitectureInterface
from rottnest.server.controller_mapper import ControllerMapper

class ArchitectureControllerTests(unittest.TestCase):
    '''
       Testing the architecture controller route
    '''

    ENDPOINT_DATA_MAP = {
        'arch.get_list': { },
        'arch.get_current': {  },
        'arch.set_current': { 'architecture_key' : "NoArch" },
        'arch.set_config': { 'architecture_config' : {} } ,
        'arch.get_config': {  }
    }

    @staticmethod
    def err_fn():
        '''
           Error function - Will failure/return false 
        '''
        return False

    @staticmethod
    def endpoint_check(endpoints, cls_obj_list):
        '''
           Endpoint Checking - Iterates through the list of endpoints and data
           payloads to then check if all the methods can be serialised 
        '''
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
                                              ArchitectureControllerTests.err_fn)
            # NOTE: Will reserve this for other test objects
            mapobj = mapper_fn(ArchitectureInterface, message)
            assert mapper_fn is not None
            assert hasattr(mapper_fn, '__call__')
            assert mapobj is not None
            assert isinstance(mapobj, str)

    @staticmethod
    def check_controller_method(message_str, controller_callable):
        '''
           Generalised method for the tests, processes the controller methods
           and serialises the data 
        '''

        
        message_payload = ArchitectureControllerTests.ENDPOINT_DATA_MAP[message_str]
        messageobj = {
            "message": message_str,
            "payload": message_payload
        }
        
        result = controller_callable(messageobj)

        assert result is not None
        assert isinstance(result.serialize(lambda r : json.dumps(r)), str)

    def test_mapper_get_all_serialisable(self):
        '''
           Goes through all the endpoints as if the websocket
           is utilising it, and ensures that data returned is
           serialised 
        '''
        
        endpoints = map(lambda e : e, ArchitectureControllerTests.ENDPOINT_DATA_MAP\
                        .items())
        ArchitectureControllerTests.endpoint_check(endpoints,
                                                   [ArchitectureInterface])
        
    
    def test_get_list_and_serialisable(self):
        '''
           Tests retrieving the list of serialised architectures 
        '''
        message_str = 'arch.get_list'
        ArchitectureControllerTests.check_controller_method(message_str,
            lambda msg : ArchitectureInterface.get_architecture_list(msg))


    def test_get_current_and_serialisable(self):
        '''
           Retrieves the current config as a serialised
           set of data 
        '''
        message_str = 'arch.get_current'
        ArchitectureControllerTests.check_controller_method(message_str,
            lambda msg : ArchitectureInterface.get_current_architecture(msg))


    def test_get_current_config_and_serialisable(self):
        '''
           When given an architecture, confirmation should be sent
           back to confirm it has been set 
        '''
        message_str = 'arch.get_config'
        ArchitectureControllerTests.check_controller_method(message_str,
            lambda msg : ArchitectureInterface.get_architecture_config(msg))

    def test_set_current_config_confirmation_and_serialisable(self):
        '''
           When set, the message returned should be confirmation
           of the configuration 
        '''
        message_str = 'arch.set_current'
        ArchitectureControllerTests.check_controller_method(message_str,
            lambda msg : ArchitectureInterface.set_architecture(msg))


    # def test_bad_set_architecture_rejection_and_serialisable():
    #     '''
    #        When given a plugin or data that is not appropriate, the system
    #        should reject the architecture and send an appropriate message
    #        back to the client
    #     '''
    #     pass

    # def test_bad_set_config_rejection_and_serialisable():
    #     '''
    #       When given a bad configuration the server should reject
    #       the configuration and send back the appropriate message to
    #       the client  
    #     '''

    #     pass
