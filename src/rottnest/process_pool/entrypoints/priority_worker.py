'''
    Priority process entrypoint
'''

# For now this is identical to the pool worker
from .pool_worker import entrypoint as worker_entrypoint

def entrypoint(*args, **kwargs):
    '''
        Entrypoint for the priority worker
    '''
    return worker_entrypoint(*args, **kwargs)
