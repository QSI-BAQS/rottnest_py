import json

from t_scheduler import ScheduleOrchestrator
from t_scheduler.base.util import make_gates, dag_create
from t_scheduler.templates.generic_templates import make_explicit
from t_scheduler.base.gate_additional import BellGate

from graph_state_generation.mappers import weight_sort_mapper 
from graph_state_generation.schedulers import greedy_cz_scheduler
from graph_state_generation.graph_state import example_graphs

from ..region_builder.json_to_region import json_to_layout, example as example_region_obj

from .t_orchestrator import t_orchestration
from .graph_state_orchestrator import graph_state_orchestration, cabaliser_to_graph_state
#from .bell_orchestrator import bell_orchestrator
from .gate_construction import make_pseudo_gates
from rottnest.gridsynth.gridsynth import Gridsynth

# print("Gridsynth load path:",Gridsynth.GATE_SYNTH_BNR)
shared_gridsynth = None

def make_mapper(graph_state, reg_region_obj):

    height = reg_region_obj['height']
    width = reg_region_obj['width']
    spacing = 2 # TODO move into front end option

    if reg_region_obj['region_type'] == 'CombShapedRegisterRegion':
        mapped_gs = weight_sort_mapper.CombWeightSortMapper(graph_state, height, width, comb_spacing = spacing, n_passes=100)
    else:
        mapped_gs = weight_sort_mapper.LinearWeightSortMapper(graph_state)

    return mapped_gs


def run_widget(cabaliser_obj=None, region_obj=None, full_output=False, rz_tag_tracker=None):
    # TODO delete after testing passes
    if cabaliser_obj is None:
        with open('qft_test_obj.json') as f:
            cabaliser_obj = json.load(f)
    
    if region_obj == None:
        region_obj = example_region_obj
    for key, val in cabaliser_obj['adjacencies'].items():
        for x in val:
            if key not in cabaliser_obj['adjacencies'][x]:
                cabaliser_obj['adjacencies'][x].append(key)
                cabaliser_obj['adjacencies'][x].sort()
    for key, val in cabaliser_obj['adjacencies'].items():
        cabaliser_obj['adjacencies'][key] = sorted(set(val))

    # Load Gates
    # gates = make_gates(cabaliser_obj)
    # dag_layers, all_gates = dag_create(cabaliser_obj, gates)
    # dag_roots = dag_layers[0]
    global shared_gridsynth
    if shared_gridsynth is None:
        shared_gridsynth = Gridsynth()

    dag_roots = make_pseudo_gates(cabaliser_obj, shared_gridsynth, rz_tag_tracker)

    # print("roots", dag_roots)
    # Load layout
    layout = json_to_layout(region_obj)
    strategy, widget = make_explicit(layout, region_obj['width'], region_obj['height'])
    
    graph_state = cabaliser_to_graph_state(cabaliser_obj) 

    temp_reg_region = region_obj['regions'][0]# TODO delete
    strategy.mapper = make_mapper(graph_state, temp_reg_region) # TODO gosc mapper
    
    orc = ScheduleOrchestrator(dag_roots, widget, strategy, json=full_output)

    # Graph State Scheduler
    try:
        graph_state_orchestration(orc, graph_state)  
    except Exception as e:
        import traceback
        import sys
        traceback.print_exc(file=sys.stderr)
        print(cabaliser_obj, file=sys.stderr)
        try:
            tb = traceback.format_exception(e)
            # Debug output exceptions
            with open('errors.out', 'a') as f:
                print('=============file===========', file=f)
                print(cabaliser_obj, file=f)
                print('=============tb===========', file=f)
                print(''.join(tb), file=f)
        except:
            pass

    bell_in = [BellGate(targ) for targ in cabaliser_obj["statenodes"] if targ is not None]
    bell_out = [BellGate(targ, is_input=False) for targ in cabaliser_obj["outputnodes"] if targ is not None]

    orc.run_bell(bell_in)

    # T scheduler
    t_orchestration(orc)

    orc.run_bell(bell_out)

    return orc
