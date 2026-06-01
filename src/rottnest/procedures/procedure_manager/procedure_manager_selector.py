from .concurrent_procedure_manager import ConcurrentProcedureManager
from .serial_procedure_manager import SerialProcedureManager
from .procedure_manager import ProcedureManager


class DoubleInitialisationException(Exception):
    '''
       Attempting to initialise the selector multiple time
       This should be disallowed 
    '''

    DOUBLE_INIT_TEXT = 'Attempting to initialise twice'
        
    def __init__(self):
        super().__init__(DoubleInitialisationException.DOUBLE_INIT_TEXT)

class ProcedureManagerSelector:
    '''
        Manager selector, used to provide singleton instances that
        can be used by other components of the codebase

        This in its own right is a singleton instance that can be
        access in other places

        It provides a class level interface as well
    '''

    # Selector instance itself
    _selector_instance = None

    def __init__(self):
        '''
           Initialises a new object selector
           Will throw an exception if the selector is attempting
           to initialise twice 
        '''
        self.concurrent_instance = None
        self.serial_instance = None

        if ProcedureManagerSelector._selector_instance is None:
            ProcedureManagerSelector._selector_instance = self
        else:
            raise DoubleInitialisationException()

    @classmethod
    def get_default_procedure_manager(context: object | None=None):
        '''
           Gets the default procedure manager 
        '''
        instance = ProcedureManagerSelector.get_instance()
        return instance.get_concurrent_manager(context)          

    @classmethod
    def get_instance(cls) -> 'ProcedureManagerSelector':
        '''
           Gets the instnace of the selector itself 
        '''
        if ProcedureManagerSelector._selector_instance is None:
            ProcedureManagerSelector._selector_instance = \
                ProcedureManagerSelector()
        return ProcedureManagerSelector._selector_instance

    def get_default(self, app: object | None = None) -> ProcedureManager:
        '''
           Will return the ConcurrentProcedureManager for now
               Will allow for configuration later on
        '''
        return self.get_concurrent_manager(app)
        
        
    def get_concurrent_manager(self, app: object | None) -> ConcurrentProcedureManager:
        '''
           Gets the concurrent manager
           This will maintain the instance itself 
        '''
        if self.concurrent_instance is None:
            self.concurrent_instance = ConcurrentProcedureManager(app)
            self.concurrent_instance.start_manager_in_thread()

        return self.concurrent_instance
        
    def get_serial_manager(self, app: object | None) -> SerialProcedureManager:
        '''
           Gets the serial manager
           This wil maintain the instance itself 
        '''
        if self.serial_instance is None:
            self.serial_instance = SerialProcedureManager(app)
            self.serial_instance.start_manager_in_thread()
            

        return self.serial_instance
        
