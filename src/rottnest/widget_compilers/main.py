from t_scheduler import ScheduleOrchestrator
from t_scheduler.base.util import make_gates, dag_create
from t_scheduler.templates.generic_templates import make_explicit
import json

from ..region_builder.json_to_region import json_to_layout, example as example_region_obj

# TODO delete after testing
def test_mapper():
    from graph_state_generation.mappers import weight_sort_mapper 
    from graph_state_generation.schedulers import greedy_cz_scheduler
    from graph_state_generation.graph_state import example_graphs

    height = 10
    width = 10
    spacing = 2

    n_vertices = 50
    gs = example_graphs.graph_binary_tree(n_vertices)

    mapped_gs = weight_sort_mapper.CombWeightSortMapper(gs, height, width, comb_spacing = spacing, n_passes=100)
    # schedule = greedy_cz_scheduler.GreedyCZScheduler(gs, mapped_gs) 
    return mapped_gs


def run(gate_obj=None, region_obj=None):
    # TODO delete after testing passes
    with open('qft_test_obj.json') as f:
        gate_obj = json.load(f)
    region_obj = example_region_obj

    # Load Gates
    gates = make_gates(gate_obj)
    dag_layers, all_gates = dag_create(gate_obj, gates)
    dag_roots = dag_layers[0]


    # Load layout
    layout = json_to_layout(region_obj)
    strat, widget = make_explicit(layout, region_obj['width'], region_obj['height'])
    
    strat.mapper = test_mapper() # TODO gosc mapper

    orc = ScheduleOrchestrator(dag_roots, widget, strat, json=True)
    orc.schedule()

    return orc