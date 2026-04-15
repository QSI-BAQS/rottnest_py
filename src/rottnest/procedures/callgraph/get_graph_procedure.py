from rottnest.procedures import procedure
from rottnest.process_pool.singleton import get_pool

STAGE_TAG = 'get_graph_procedure'

class GetGraphProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(self, *, tag=TAG, dependencies=None, asynchronous=True,\
                 graph_id=None, results_ref: None | dict =None):

        self.results_ref = dict()
        if results_ref is not None:
            self.results_ref = results_ref

        self.graph_id = graph_id
        self._complete = False
        stages = []
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)

    @classmethod
    def construct_get_graph_proc(cls, results_ref: dict, graph_id: None | int =None):
        '''
           Factory method for constructing the procedure for this stage 
        '''
        return GetGraphProcedure(graph_id=graph_id, results_ref=results_ref)


    def try_retrieve(self, compiler_environment=None, reporting=True, single_pass=False):
        '''
           Attempts to retrieve the callgraph but may not eb able to do it immediately. 
        '''
        
        graph_id = self.graph_id
        pool_manager = get_pool()
        callgraph_results = pool_manager.get_callgraph(graph_id)

        if callgraph_results is None:
            return False
        else:
            self.results_ref['graph'] = callgraph_results
            return True
        

    def execute(self, compiler_environment=None, reporting=True, single_pass=False)\
         -> bool | None:
        '''
           Executes/Dispatches a task to operate on the process pool
               - Get the process pool object
               - Then afterwards, it will have some capability to query the
                   the process pool to extract a graph object 
        '''
        self._complete = self.try_retrieve()
        

    def poll(self):
        '''
        Polling to check to see if we are to perform a transformation or
        even update the current procedure completion
        '''
        self._complete = self.try_retrieve()
        
        
    def complete(self):
        '''
           Checks to see if the current procedure is complete or not 
        '''
        return self._complete
