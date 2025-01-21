from t_scheduler.base import util, util_additional

from t_scheduler.widget import CombShapedRegisterRegion, SingleRowRegisterRegion
from graph_state_generation.graph_state.graph_state import GraphState
from graph_state_generation.schedulers.greedy_cz_scheduler import GreedyCZScheduler 

graph_state_schedulers = { 
    CombShapedRegisterRegion: GreedyCZScheduler,
    SingleRowRegisterRegion: GreedyCZScheduler 
}

# Todo, move this to some cost dictionary
CYCLES_PER_CZ = 4


# TODO: genericise for either json or direct cabaliser object 
def cabaliser_to_graph_state(cabaliser_obj: dict) -> GraphState:
    '''
        Constructs a graph state object from a cabaliser json dict
    '''
    n_vertices = cabaliser_obj['n_qubits']
    gs = GraphState(n_vertices)
    for node, adj in cabaliser_obj['adjacencies'].items():
        node = int(node)
        gs[node].append(adj)
    return gs

def graph_state_orchestration(orc, graph_state):
    '''
        Runs the graph state scheduler
    '''
    strategy = orc.strategy
    register = strategy.register_router.region
    mapper = strategy.mapper

    gs_scheduler = graph_state_schedulers[register.__class__](graph_state, mapper)
    dag = util_additional.make_gsprep_layers(gs_scheduler.flatten())

    orc.prepare_gs(dag[0])

    return gs_scheduler
