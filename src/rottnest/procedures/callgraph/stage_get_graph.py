from rottnest.procedures import stage
from rottnest.process_pool.singleton import get_pool


STAGE_TAG = 'get_graph'

class GetGraphStage(stage.RottnestCompilerStage): 

    TAG = STAGE_TAG

    def __init__(self, 
        graph_id=None,
        tag=None,
        dependencies=None
    ):
        self.graph_id = graph_id
        self._callgraph_results = None
        super().__init__(asynchronous=True)

    def execute(
            self,
            compiler_environment=None,
        ) -> bool | None:
        '''
           Executes/Dispatches a task to operate on the process pool
               - Get the process pool object
               - Then afterwards, it will have some capability to query the
                   the process pool to extract a graph object 
        '''
        pool = get_pool()
        pool.get_callgraph(self.graph_id)
        
    def poll(self, compiler_environment):
        '''
            Poll
        '''
        if self._complete:
            return

        pool = get_pool()
        callgraph_results = pool.get_callgraph_status()

        if callgraph_results is not None: 
            self._complete = True
            self._callgraph_results = callgraph_results

    def __call__(self):
        '''
            Binding for namespace in environment
        '''
        return self._callgraph_results
        
