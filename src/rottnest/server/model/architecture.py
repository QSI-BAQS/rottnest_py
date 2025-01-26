from functools import lru_cache
import json
import random
from typing import Any
import threading

# Ill advised, but forces the generation and capture of the region types
from t_scheduler.region import * 
from t_scheduler.region.region_types import region_types, region_args

from t_scheduler.router import *
from t_scheduler.router import region_router_exports

from rottnest.widget_compilers.main import run as run_widget
from rottnest.process_pool import process_pool

# TODO: Unbind references from here
from rottnest.compute_units.architecture_proxy import saved_architectures

from rottnest.input_parsers.cirq_parser import shared_rz_tag_tracker

# saved_architectures: Dict[int, arch_json_obj | ArchProxyObj]
# arch_json_obj is json from front end

from rottnest.process_pool.process_pool import ComputeUnitExecutorPool
cu_executor_pool = ComputeUnitExecutorPool()

@lru_cache
def get_region_subtypes() -> str: 
    '''
        Extracts the region subtypes from the t_scheduler
        Exposes the names of the regions as a json object
    '''
    # Import architecture, get subtype names
    return {i: list(region_types[i].keys()) for i in region_types}
   
def get_factory_types() -> str: 
    return ''

def log_resp(resp: Any):
    resp_log = str(resp)
    if len(resp_log) > 200:
        resp_log = resp_log[:200] + '<... output truncated>'
    print("Resp:", resp_log)

# TODO reorganise this mess and cull unused

def run_widget_pool(arch_id):
    print("in run_widget_pool")
    # TODO use more than single object here
    cu_executor_pool.run_sequence([arch_id])
    t = threading.Thread(target=_read_results, name="ResultReaderThread", args=[cu_executor_pool], daemon=True)
    t.start()


def _read_results(pool):
    while True:
        result = pool.manager_completion_queue.get()
        # print("Got thread result", result)
        # TODO handle results in this thread


def run_debug(arch_id, wsock):
    it = ComputeUnitExecutorPool._run_sequence([arch_id])
    # compute_unit = next(it)[0]
    for obj in it:
        if len(shared_rz_tag_tracker._tags_to_angles) > 3:
            wid = obj[0].compile_graph_state()
            if max(wid.get_measurement_tags()) >= 3:
                print("tags are", list(wid.get_measurement_tags()))
                break
    compute_unit = obj[0]
    print("tag tracker", shared_rz_tag_tracker._tags_to_angles)
    cu_executor_pool.run_priority(compute_unit, shared_rz_tag_tracker, True)
    result = cu_executor_pool.manager_priority_completion_queue.get()
    print("priority test got result", str(result)[:200], "<...truncated>")
    if 'traceback' in result:
        print(''.join(result['traceback']))
    wsock.send(json.dumps({
        "message": "run_result",
        "payload": result,
    }))
# END mess

def get_router_mapping():
    return region_router_exports

def save_arch(arch_json_obj):
    arch_id = random.randint(1000000, 9999999)
    while arch_id in saved_architectures: arch_id = random.randint(1000000,
                                                                   9999999)

    saved_architectures[arch_id] = arch_json_obj
    cu_executor_pool.save_arch(arch_id, arch_json_obj)
    return arch_id

def retrieve_graph_segment(gid):
    #TODO: Please finish this, not sure what you'd want
    # Provided example layout
    return { 
            "root_index" : 0,
            "graph" : [ 
                {
                        "name" : "start",
                        "description" : "simple thing",
                        "children" : [1, 2]
                    },
                    {
                        "name" : "c1",
                        "description" : "child 1",
                        "children" : []
                    },
                    {
                        "name" : "c2",
                        "description" : "child 2",
                        "children" : []
                    },

                ]
            }

def get_region_arguments():
    return region_args


def get_status(cu_id):
    return {'cu_id': cu_id, 'status': 'not_found'}
    if cu_id in process_pool.dummy_result_cache:
        return process_pool.dummy_result_cache[cu_id]
    else:
        return {'cu_id': cu_id, 'status': 'not_found'}
