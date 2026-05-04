'''
   Operations Specification that will check as part of its construction 
'''

from rottnest.server.protocol.operation import Noop

class WebSocketOperationSpecException(Exception):
    '''
       Raises an exception is the operations are not detected 
    '''
    def __init__(self, method_name):
        super().__init__(f"Error, Method '{method_name}' is missing from class")

class WebSocketOperationsSpecification:
    '''
       Specification that is used by a operations object
       to ensure that it adheres to the specification on
       construction

       This will check to see if a relevant method exists 
    '''
    OPERATIONS = Noop
    

    def __init__(self, operation_type: type['WebSocketOperationsSpecification']):
        '''
           Specification of the websocket to ensure that
           the correct network

           During initialisation - Evaluate if the spec is
           being honoured here

           raise exception if it isn't

           Extensions:
               * Ensure types also have the correct mapping for the methods
                   as well
               * Makes sure the operations as part of the specification
                   have A implementation
        '''
        self._detect_operations(operation_type)

    @classmethod
    def get_operations_data(cls):
        '''
           Gets the operations data from the object itself 
        '''
        return cls.OPERATIONS.to_list()

    def _detect_operations(self, operation_type: 'WebSocketOperationsSpecification'):
        '''
           Checks to see if the object has the operations specified 
        '''

        for method in operation_type.get_operations_data():
            if getattr(operation_type, method, None) is None:
                '''
                   Type is missing the necessary methods 
                '''
                raise WebSocketOperationSpecException(method)
            
