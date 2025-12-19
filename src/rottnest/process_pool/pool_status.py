'''
    Simple shared enum for pool statusing
'''


class PoolStatus:
    '''
        Namespacing class
        Not quite an ENUM
    '''
    UNSTARTED = 'UNSTARTED'
    STARTING = 'UNSTARTED'
    IDLE = 'IDLE'
    SYNCHRONISING = 'SYNCHRONISING'
    PREPROCESSING = 'PREPROCESSING'
    EXECUTING = 'EXECUTING'
    FINISHED = 'FINISHED'
