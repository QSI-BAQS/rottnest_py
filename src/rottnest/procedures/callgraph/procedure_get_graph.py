from rottnest.procedures import procedure
from rottnest.process_pool.singleton import get_pool
from rottnest.debug.util import with_debug_log
from rottnest.procedures.procedure_manager import MPSCChannelProvider, MPSC_CALLGRAPH_CHANNEL_TAG

STAGE_TAG = 'get_graph_procedure'

class GetGraphProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(self, *, tag=TAG, dependencies=None, asynchronous=True,\
                 graph_id=None):


        self.graph_id = graph_id
        self._complete = False
        self._was_aborted = False
        stages = []

        mpsc_provider = MPSCChannelProvider.get_instance()
        self._writer, _mpscstate = mpsc_provider.get_writer(MPSC_CALLGRAPH_CHANNEL_TAG)

        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)


    @with_debug_log()
    def abort_procedure(self):
        '''
        '''
        self._complete = True
        self._was_aborted = True

    @with_debug_log()
    def was_aborted(self):
        '''
           Checks to see if the procedure was aborted 
        '''
        return self._was_aborted

    @with_debug_log()
    def try_retrieve(self, compiler_environment=None, reporting=True, single_pass=False):
        '''
           Attempts to retrieve the callgraph but may not eb able to do it immediately. 
        '''
        
        pool = get_pool()

        callgraph_results = pool.get_callgraph_status()

        if callgraph_results is None:
            return False
        else:
            self._writer.write(callgraph_results)
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
        
    @with_debug_log()
    def poll(self):
        '''
        Polling to check to see if we are to perform a transformation or
        even update the current procedure completion
        '''
        if self._complete is not True:
            self._complete = self.try_retrieve()
        
    @with_debug_log()
    def complete(self):
        '''
           Checks to see if the current procedure is complete or not 
        '''
        return self._complete
