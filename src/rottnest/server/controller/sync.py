'''
   Simple CRUD for state and synchronisation
   Most of the logic is in the frontend 
'''

from rottnest.server.interface_spec.route_interface import RouteInterface

from rottnest.server.util.result import Result
from rottnest.server.model import sync as model 

MODULE_PREFIX = 'sync'
GET_STATE_SUFFIX = 'get'
SET_STATE_SUFFIX = 'set'

SYNCHRONISE_PAYLOAD = 'payload'

class SynchroniseInterface(RouteInterface):
    '''
       Synchronisation interface, used to outline what
       the interaction with the frontend and backend and ensuring the
       state can be restored from a local version
    '''

    @RouteInterface.bind_route(MODULE_PREFIX, GET_STATE_SUFFIX)
    @classmethod
    def get_state(cls, message, **kwargs) -> Result:
        '''
           Gets the state that is saved 
        '''

        res = model.sync_get_state()
        return Result.Ok(res)

    @RouteInterface.bind_route(MODULE_PREFIX, SET_STATE_SUFFIX)
    @classmethod
    def set_state(cls, message, **kwargs) -> Result:
        '''
           Sets the state that can be retrieved 
        '''
        payload = message[SYNCHRONISE_PAYLOAD]
        res = model.sync_set_state(payload)
        return Result.Ok(res)
        
