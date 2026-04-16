from rottnest.procedures import procedure
from rottnest.process_pool.singleton import get_pool

STAGE_TAG = 'get_graph_procedure'

RESULTS_KEY = 'graph_results'

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


    def abort_procedure(self):
        '''
           Override for the complete if set by the procedure manager 
        '''
        self._complete = True

    def try_retrieve(self, compiler_environment=None, reporting=True, single_pass=False):
        '''
           Attempts to retrieve the callgraph but may not eb able to do it immediately. 
        '''
        
        pool = get_pool()

        callgraph_results = pool.get_callgraph_status()

        if callgraph_results is None:
            return False
        else:
            self.results_ref[RESULTS_KEY] = callgraph_results
            return True
        

    def execute(self, compiler_environment=None, reporting=True, single_pass=False)\
         -> bool | None:
        '''
           Executes/Dispatches a task to operate on the process pool
               - Get the process pool object
               - Then afterwards, it will have some capability to query the
                   the process pool to extract a graph object 
        '''
        graph_id = self.graph_id
        pool = get_pool()
        pool.get_callgraph(graph_id)
        

    def poll(self):
        '''
        Polling to check to see if we are to perform a transformation or
        even update the current procedure completion
        '''
        if self._complete is not True:
            self._complete = self.try_retrieve()
        
        
    def complete(self):
        '''
           Checks to see if the current procedure is complete or not 
        '''
        return self._complete
