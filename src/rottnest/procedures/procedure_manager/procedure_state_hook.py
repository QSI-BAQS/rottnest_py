

class ProcedureStateHook:
    '''
       ProcedureStateHook
       Hooks into a procedure object to separate away
       predefined procedures, state and completion - this means
       the events for:
           * poll
           * complete

        Are given as a callback via this hook's construction
        and used during an abstracted call on poll and complete

    '''

    def __init__(self, state_obj=dict(),
                 poll_callback=None,
                 complete_callback=None,
                 finaliser_callback=None,
                 procedure_tup=None):
        '''
            Since the state object itself takes any kind
            of data, the poll_callback and complete_callback
            must be aware of how it works.
        '''
        
        self.state_object = state_obj
        self.poll_callback = poll_callback
        self.complete_callback = complete_callback
        self.finaliser_callback = finaliser_callback

    def get_complete_callback(self):
        '''
            Gets the complete callback attached to the object
        '''
        return self.complete_callback

    def get_poll_callback(self):
        '''
            Gets the poll callback attached to the object
        '''
        return self.poll_callback

    def get_finaliser_callback(self):
        '''
           Gets the finaliser callback attached to the object 
        '''
        return self.finaliser_callback

    def get_state_object(self):
        '''
           Gets the state object associated with the object 
        '''
        return self.state_object
    
