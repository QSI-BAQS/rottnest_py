'''
    Generic status decorator
'''
import abc

def status_update(status, post_status):
    '''
        Status update decorator factory
    '''
    def _wrap_fn(fn):
        '''
            Decorator wrapper
        '''
        def _wrap(self, *args, **kwargs):
            '''
                Decorator resolver
            '''
            self.set_status(status)

            print("DEBUG STATUS UPDATE: ", status)
            result = fn(self, *args, **kwargs)
            self.set_status(post_status)
            print("DEBUG STATUS UPDATE: ", post_status)

            return result
        return _wrap 
    return _wrap_fn

class StatusTracked(abc.ABC):
    '''
        Abstract base class for status tracking
    '''
    def set_status(self, status):
        '''
            Abstract status setter
        '''

    def get_status(self):
        '''
            Abstract status getter
        '''
