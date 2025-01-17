from t_scheduler import ScheduleOrchestrator
from t_scheduler.base.util import make_gates, dag_create
from t_scheduler.templates.generic_templates import make_explicit
import json

from ..region_builder.json_to_region import json_to_layout, example as example_region_obj

# TODO delete after testing
def test_comb_mapper(n_vertices, width, height, spacing=2):
    from graph_state_generation.mappers import weight_sort_mapper 
    from graph_state_generation.schedulers import greedy_cz_scheduler
    from graph_state_generation.graph_state import example_graphs

    gs = example_graphs.graph_binary_tree(n_vertices)
    mapped_gs = weight_sort_mapper.CombWeightSortMapper(gs, height, width, comb_spacing = spacing, n_passes=100)
    # schedule = greedy_cz_scheduler.GreedyCZScheduler(gs, mapped_gs) 
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
    strat.mapper = test_comb_mapper(gate_obj['n_qubits'], temp_reg_region['width'], temp_reg_region['height']) # TODO gosc mapper

    orc = ScheduleOrchestrator(dag_roots, widget, strat, json=True)
    orc.schedule()

    return orc