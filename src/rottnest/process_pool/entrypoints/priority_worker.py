'''
    Priority process entrypoint
'''

# For now this is identical to the pool worker
from rottnest.process_pool.entrypoints.pool_worker import get_entrypoint as get_worker_entrypoint

def get_entrypoint(*args, **kwargs):
    '''
        Entrypoint for the priority worker
    '''
    return get_worker_entrypoint(*args, **kwargs)
