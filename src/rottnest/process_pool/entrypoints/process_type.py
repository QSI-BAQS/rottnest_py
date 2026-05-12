SERVER = 'SERVER'
POOL_MANAGER = 'POOL_MANAGER'
POOL_WORKER = 'POOL_WORKER'
POOL_PRIORITY_WORKER = 'POOL_PRIORITY_WORKER'
RZ_DECOMPOSER = 'RZ_DECOMPOSER'

class ProcessType():
    TYPE = None

    # Rules for spawning processes
    SPAWN_RULES = {
        None: [POOL_MANAGER],
        SERVER: [POOL_MANAGER],
        POOL_MANAGER: [
            POOL_WORKER,
            POOL_PRIORITY_WORKER
        ],
        POOL_WORKER: [RZ_DECOMPOSER],
        POOL_PRIORITY_WORKER: [RZ_DECOMPOSER]
    }
    
    @classmethod
    def get_type(cls):   
        '''
            Getter
        '''
        return cls.TYPE

    @classmethod
    def set_type(cls, process_type):
        '''
            Setter
        '''
        # Check that the type of the process has not changed
        # Allow duplicate setting
        assert cls.TYPE is None or cls.TYPE == process_type

        # Check that the process type is valid
        assert process_type in cls.SPAWN_RULES
        cls.TYPE = process_type

    @classmethod
    def validate(cls, spawn_type):
        '''
            Valides the type of the spawning process
            Against the permitted rules
        '''
        process_type = cls.get_type()
        # Check that a rule exists permitting the
        # spawn type 
        assert (
            spawn_type in cls.SPAWN_RULES[process_type]
        )

def get_type():
    '''
        Dispatch for singleton getter
    '''
    return ProcessType.get_type()

def set_type(process_type):
    '''
        Dispatch for singleton setter
    '''
    return ProcessType.set_type(process_type)

def validate(spawn_type): 
    '''
        Validates the type of process to be spawned
        Dispatch to singleton validation
    '''
    ProcessType.validate(spawn_type)
