import json
import threading

from rottnest.process_pool import process_pool
from rottnest.compute_units.layout_proxy import LayoutProxy 
from rottnest.process_pool.process_pool import ComputeUnitExecutorPool



# TODO: May want to get a shared unit instead of instantiating it
# here

cu_executor_pool = ComputeUnitExecutorPool()   

def log_resp(resp):
    resp_log = str(resp)
    if len(resp_log) > 200:
        resp_log = resp_log[:200] + '<... output truncated>'
    print("Resp:", resp_log)


# TODO reorganise this mess and cull unused
def run_widget_pool(arch_id, wsock=None, wsock_sem=None):
    print("in run_widget_pool")
    from rottnest.plugins import architectures, executables

    # TODO use more than single object here
    cu_executor_pool.synchronise()
    cu_executor_pool.set_executable(executables.get_current_executable().get_name())
    cu_executor_pool.set_executable_params(executables.get_current_executable_args())

    cu_executor_pool.set_architecture_module(architectures.get_current_architecture().get_name())
    
    cu_executor_pool.start_workers()
    cu_executor_pool.run_sequence([arch_id])
    
    #print(str(cu_executor_pool))

    print(arch_id)
    print(architectures.get_current_architecture())
    print(executables.get_current_executable())

    t = threading.Thread(target=_read_results, name="ResultReaderThread", args=[cu_executor_pool, wsock, wsock_sem], daemon=True)
    t.start()


def _read_results(pool, wsock=None, wsock_sem=None):
    # TODO: remove this file, use a pipe
    with open("stream_output.json", "w") as f:
        while True:
            result = pool.manager_completion_queue.get()
            if result == 'done':
                print('reader thread exiting')
                break
            # print("Got thread result", str(result))
            if 'cache_hash' in result:
                del result['cache_hash']

            if result.get("cu_id", "") == "TOTAL":
                json.dump(result, f)
                print(file=f)
            with wsock_sem:
                wsock.send(json.dumps({
                    'message': 'data_run_result',
                    'payload': result,
                }))
            # TODO handle results in this thread


def save_arch(layout_obj):
    """
        Hook to the layout proxy singleton
    """
    layout_id = LayoutProxy.add_layout(layout_obj)
    return layout_id 

def _read_root_graph(pool, wsock=None, wsock_sem=None):
    """
       TODO: We need to remove this or make it cater to
       a generic architecture infrastructure 
    """
    graph_object = pool.manager_priority_completion_queue.get()
    with wsock_sem:
        wsock.send(json.dumps({
                'message': 'data_get_root_graph',
                'payload' : {
                    'gid' : 'cg', #super silly
                    'graph_view' : graph_object 
                }
            }))
    print("Get root graph completed!")

def get_root_graph(wsock, wsock_sem=None):
    """
       Gets the root_graph within the call_graph
       Although, call_graph mechanisms have not been outlined
       yet for generic_architecture

       TODO: Revise on get_root_graph and the protocol 
    """

    cu_executor_pool.get_graph(None)
    t = threading.Thread(target=_read_root_graph, name="GraphResultReaderThread", args=[cu_executor_pool, wsock, wsock_sem], daemon=True)
    t.start()


def get_status(cu_id):
    """
       Designed to return the compute unit id,
       however the early return makes the rest of the function useless.

       This has been removed for now
    """
    if cu_id in process_pool.dummy_result_cache:
        return process_pool.dummy_result_cache[cu_id]
    else:
        return {'cu_id': cu_id, 'status': 'not_found'}
