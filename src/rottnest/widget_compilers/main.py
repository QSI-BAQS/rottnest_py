from t_scheduler import ScheduleOrchestrator
from t_scheduler.base.util import make_gates, dag_create
from t_scheduler.templates.generic_templates import make_explicit
import json

from ..region_builder.json_to_region import json_to_layout, example as example_region_obj

def make_mapper(gate_obj, reg_region_obj):
    from graph_state_generation.mappers import weight_sort_mapper 
    from graph_state_generation.schedulers import greedy_cz_scheduler
    from graph_state_generation.graph_state import example_graphs
    from graph_state_generation.graph_state.graph_state import GraphState

    height = reg_region_obj['height']
    width = reg_region_obj['width']
    spacing = 2 # TODO move into front end option
    n_vertices = gate_obj['n_qubits']

    gs = GraphState(n_vertices)
    for node, adj in gate_obj['adjacencies'].items():
        node = int(node)
        gs[node].append(adj)

    if reg_region_obj['region_type'] == 'CombShapedRegisterRegion':
        mapped_gs = weight_sort_mapper.CombWeightSortMapper(gs, height, width, comb_spacing = spacing, n_passes=100)
    else:
        mapped_gs = weight_sort_mapper.LinearWeightSortMapper(gs)


    return mapped_gs


def run(gate_obj=None, region_obj=None):
    # TODO delete after testing passes
    with open('qft_test_obj.json') as f:
        gate_obj = json.load(f)
    
    if region_obj == None:
        region_obj = example_region_obj

    # Load Gates
    gates = make_gates(gate_obj)
    dag_layers, all_gates = dag_create(gate_obj, gates)
    dag_roots = dag_layers[0]


    # Load layout
    layout = json_to_layout(region_obj)
    strat, widget = make_explicit(layout, region_obj['width'], region_obj['height'])
    
    temp_reg_region = region_obj['regions'][0]# TODO delete
    strat.mapper = make_mapper(gate_obj, temp_reg_region) # TODO gosc mapper

    orc = ScheduleOrchestrator(dag_roots, widget, strat, json=True)
    orc.schedule()

    return orc