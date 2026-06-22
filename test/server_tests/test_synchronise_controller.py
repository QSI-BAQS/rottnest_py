'''
   Tests for the architecture controller, ensuring
   it meets particular criteria 
'''
import unittest
import json
import time
from rottnest.server.controller.sync import SynchroniseInterface
from rottnest.server.controller_mapper import ControllerMapper

SYNC_GET_STATE = 'sync.get'
SYNC_SET_STATE = 'sync.set'

SYNC_TIMESTAMP_KEY = 'timestamp'
SYNC_RUNCHART_KEY = 'runchart'
SYNC_LAYOUT_KEY = 'layout'
SYNC_ARCHITECTURE_KEY = 'architecture'
SYNC_EXECUTABLE_KEY = 'executable'

class SynchroniseControllerTests(unittest.TestCase):
    '''
       Testing the synchronise controller route
    '''

    @staticmethod
    def check_controller_method(message_str, controller_callable, message_payload=None):
        '''
           Generalised method for the tests, processes the controller methods
           and serialises the data 
        '''
        prefix = 'rottnest'
        message_fullname = prefix + '.' + message_str
        
        messageobj = {
            "message": message_fullname,
            "payload": message_payload
        }
        
        result = controller_callable(messageobj)

        assert result is not None
        assert SYNC_TIMESTAMP_KEY in result
        assert SYNC_RUNCHART_KEY in result
        assert SYNC_LAYOUT_KEY in result
        assert SYNC_EXECUTABLE_KEY in result
        assert SYNC_ARCHITECTURE_KEY in result
        assert isinstance(result.serialize(lambda r : json.dumps(r)), str)

    @staticmethod
    def make_default_state():
        '''
           Makes a default state for the sync state to be manipulated afterwards 
        '''

        SYNC_STATE_DEFAULT = {
            SYNC_TIMESTAMP_KEY: 0,
            SYNC_LAYOUT_KEY: { 'hash': '0' },
            SYNC_ARCHITECTURE_KEY:{ 'hash': '0' },
            SYNC_EXECUTABLE_KEY: { 'hash': '0' },
            SYNC_RUNCHART_KEY: { 'hash': '0' },
        }
        return SYNC_STATE_DEFAULT

    def test_get_default_state(self):
        '''
           Just tests the default state 
        '''

        
        message_str = SYNC_GET_STATE
        message_obj = {
            'message': message_str,
        }

        SynchroniseControllerTests.check_controller_method(message_str,
            lambda msg : SynchroniseInterface.get_state(message_obj))


    def test_set_state(self):
        '''
           Tests setting the value on the interface
        '''

        
        message_str = SYNC_GET_STATE
        message_payload = SynchroniseControllerTests.make_default_state()
        message_payload[SYNC_TIMESTAMP_KEY] = time.time()
        message_obj = {
            'message': message_str,
            'payload': message_payload
        }
            

        SynchroniseControllerTests.check_controller_method(message_str,
            lambda msg : SynchroniseInterface.set_state(message_obj), message_payload)
