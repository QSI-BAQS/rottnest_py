'''
   Tests for the executable controller, ensuring
   it meets particular criteria 
'''
import json
import unittest
from rottnest.server.controller.executable import ExecutableInterface
from rottnest.server.controller_mapper import ControllerMapper

from rottnest.executables.executable import RottnestExecutable
from rottnest.plugins.executable_plugins import ExecutablePlugins

import rottnest.plugins as plugins


class ExecutableDummy(RottnestExecutable):
    '''
       Creates a simple executable that can be hooked into
       the executable plugin manager and therefore used as part of the test
       cases 
    '''

    _param = None

    def n_param(self) -> int | None:
        '''
           This is a silly parameter that doesn't work
           but useful for testing 
        '''
        return self._param

    

    

class ExecutableControllerTests(unittest.TestCase):
    '''
       Testing the executable controller route
    '''

    # TODO: Maybe use the keys inside here instead of the
    #  strings
    ENDPOINT_DATA_MAP = {
        'executable.get_list': { },
        'executable.get_current': {  },
        'executable.set_current': { 'executable_key' : "NoExe",
            "executable_config": {} },
        'executable.set_config': { 'executable_config' : {} } ,
        'executable.get_config': {  }
    }

    @staticmethod
    def default_asserts():
        return [
            ExecutableControllerTests.assert_result_is_some,
            ExecutableControllerTests.assert_result_isinstance_str,
        ]

    @staticmethod
    def assert_result_is_some(result):
        '''
            Result should typically be is Some 
        '''
        assert result is not None

    @staticmethod
    def assert_result_isinstance_str(result):
        '''
           Result is being tested against the string instance 
        '''
        assert isinstance(result.serialize(lambda r: json.dumps(r)), str)

    # Above are default assert static methods
        
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
                                              ExecutableControllerTests.err_fn)
            # NOTE: Will reserve this for other test objects
            mapobj = mapper_fn(ExecutableInterface, message)

            assert mapper_fn is not None
            assert hasattr(mapper_fn, '__call__')
            assert mapobj is not None
            assert isinstance(mapobj, str)

    @staticmethod
    def check_controller_method(message_str, controller_callable, assert_ops):
        '''
           Generalised method for the tests, processes the controller methods
           and serialises the data 
        '''
        message_payload = ExecutableControllerTests.ENDPOINT_DATA_MAP[message_str]
        messageobj = {
            "message": message_str,
            "payload": message_payload
        }
        
        result = controller_callable(messageobj)

        for assert_op in assert_ops:
            assert_op(result)

       
    def test_mapper_get_all_serialisable(self):
        '''
           Goes through all the endpoints as if the websocket
           is utilising it, and ensures that data returned is
           serialised 
        '''

        exec_plugin_manager = ExecutablePlugins \
            .with_modules([])
        plugins.override_executables(exec_plugin_manager)
        
        
        endpoints = map(lambda e : e, ExecutableControllerTests.ENDPOINT_DATA_MAP.items())
        ExecutableControllerTests.endpoint_check(endpoints, [ExecutableInterface])
        
    
    def test_get_list_and_serialisable(self):
        '''
           Tests retrieving the list of serialised executable 
        '''

        assert_ops = ExecutableControllerTests.default_asserts()
        
        message_str = 'executable.get_list'
        ExecutableControllerTests.check_controller_method(message_str,
            lambda msg : ExecutableInterface.get_executable_list(msg), assert_ops)


    def test_get_current_and_serialisable(self):
        '''
           Retrieves the current config as a serialised
           set of data 
        '''
        def check_is_none(result):
            assert result.get_obj() is None

        assert_ops = [
            check_is_none
        ]
        message_str = 'executable.get_current'
        ExecutableControllerTests.check_controller_method(message_str,
            lambda msg : ExecutableInterface.get_current_executable(msg),
            assert_ops)


    def test_get_current_config_and_serialisable(self):
        '''
           When given an executable, confirmation should be sent
           back to confirm it has been set

           Params should be empty if there is no executable set
        '''
        def check_is_empty_dict(result):
            assert result.get_obj() is not None
            assert isinstance(result.get_obj(), dict)
            assert len(result.get_obj().items()) == 0

        assert_ops = [
            check_is_empty_dict
        ]
        message_str = 'executable.get_config'
        ExecutableControllerTests.check_controller_method(message_str,
            lambda msg : ExecutableInterface.get_current_config(msg), assert_ops)

    def test_set_current_config_confirmation_and_serialisable(self):
        '''
           When set, the message returned should be confirmation
           of the configuration 
        '''
        assert_ops = ExecutableControllerTests.default_asserts()
        message_str = 'executable.set_current'
        ExecutableControllerTests.check_controller_method(message_str,
            lambda msg : ExecutableInterface.set_current_config(msg), assert_ops)


    # def test_bad_set_config_rejection_and_serialisable():
    #     '''
    #       When given a bad configuration the server should reject
    #       the configuration and send back the appropriate message to
    #       the client  
    #     '''

    #     pass
