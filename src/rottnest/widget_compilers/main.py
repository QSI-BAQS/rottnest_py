import json

from t_scheduler import ScheduleOrchestrator
from t_scheduler.base.util import make_gates, dag_create
from t_scheduler.templates.generic_templates import make_explicit

from graph_state_generation.mappers import weight_sort_mapper 
from graph_state_generation.schedulers import greedy_cz_scheduler
from graph_state_generation.graph_state import example_graphs

from ..region_builder.json_to_region import json_to_layout, example as example_region_obj

from .t_orchestrator import t_orchestration
from .graph_state_orchestrator import graph_state_orchestration, cabaliser_to_graph_state
#from .bell_orchestrator import bell_orchestrator


def make_mapper(graph_state, reg_region_obj):

    height = reg_region_obj['height']
    width = reg_region_obj['width']
    spacing = 2 # TODO move into front end option

    if reg_region_obj['region_type'] == 'CombShapedRegisterRegion':
        mapped_gs = weight_sort_mapper.CombWeightSortMapper(graph_state, height, width, comb_spacing = spacing, n_passes=100)
    else:
        mapped_gs = weight_sort_mapper.LinearWeightSortMapper(graph_state)

    return mapped_gs


def run(cabaliser_obj=None, region_obj=None):
    # TODO delete after testing passes
    with open('qft_test_obj.json') as f:
        cabaliser_obj = json.load(f)
    
    if region_obj == None:
        region_obj = example_region_obj

    # Load Gates
    gates = make_gates(cabaliser_obj)
    dag_layers, all_gates = dag_create(cabaliser_obj, gates)
    dag_roots = dag_layers[0]

    # Load layout
    layout = json_to_layout(region_obj)
    strategy, widget = make_explicit(layout, region_obj['width'], region_obj['height'])
    
    graph_state = cabaliser_to_graph_state(cabaliser_obj) 

    temp_reg_region = region_obj['regions'][0]# TODO delete
    strategy.mapper = make_mapper(graph_state, temp_reg_region) # TODO gosc mapper
    
    orc = ScheduleOrchestrator(dag_roots, widget, strategy, json=True)

    # Graph State Scheduler
    graph_state_orchestration(orc, graph_state)  

    # T scheduler
    t_orchestration(orc)

    return orc
