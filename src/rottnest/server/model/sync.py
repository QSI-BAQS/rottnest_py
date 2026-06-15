'''
   Model functions that hold onto the synchronisation state
   of a client.

   If the client retrieves it, it can evict it and reset the
   the state to its own, otherwise it is assumed to be using
   the state known to the backend as well. 
'''

SYNC_DEFAULT_TIMESTAMP = 0
SYNC_DEFAULT_LAYOUT_OBJ = { 'hash' : '0' }
SYNC_DEFAULT_ARCH_OBJ = { 'hash' : '0' }
SYNC_DEFAULT_EXEC_OBJ = { 'hash' : '0' }
SYNC_DEFAULT_RUNCHART_OBJ = { 'hash' : '0' }

SYNC_TIMESTAMP_KEY = 'timestamp'
SYNC_RUNCHART_KEY = 'runchart'
SYNC_LAYOUT_KEY = 'layout'
SYNC_ARCHITECTURE_KEY = 'architecture'
SYNC_EXECUTABLE_KEY = 'executable'


'''
   Below is the sync state object that is module aligned

   This sync state is able to  
'''
SYNC_STATE = {
    SYNC_TIMESTAMP_KEY: SYNC_DEFAULT_TIMESTAMP,
    SYNC_LAYOUT_KEY: SYNC_DEFAULT_LAYOUT_OBJ,
    SYNC_ARCHITECTURE_KEY: SYNC_DEFAULT_ARCH_OBJ,
    SYNC_EXECUTABLE_KEY: SYNC_DEFAULT_EXEC_OBJ,
    SYNC_RUNCHART_KEY: SYNC_DEFAULT_RUNCHART_OBJ
}

def sync_get_state() -> dict:
    '''
       Gets the synchronisation state - the state itself
       is information that the frontend can hold onto when
       data is sent back
    '''
    return SYNC_STATE


    
def sync_set_state(data: dict) -> dict:
    '''
       Sets the synchronisation state from the frontend
    '''
    global SYNC_STATE
    SYNC_STATE = data
    return sync_get_state()
