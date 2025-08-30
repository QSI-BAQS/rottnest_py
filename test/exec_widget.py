from rottnest.widget_compilers.compiler_flow import run_widget as run_widget

from rottnest.input_parsers.cirq_parser import shared_rz_tag_tracker


def random_tags():
    tracker = shared_rz_tag_tracker.

def run_widget(widget_json, arch_json):
    '''
        Helper function, executes a widget and architecture pair
    '''

    orch = run_widget(
        cabaliser_obj=widget_json,
        region_obj=arch_json_obj,
        full_output=False,
        rz_tag_tracker=rz_tag_tracker
    )

    stats = {
        'volumes': orch.get_space_time_volume(),
        't_source': orch.get_T_stats(),
        'tocks': orch.get_tock_stats(),
        'vis_obj': None,
        'cu_id': compute_unit.unit_id,
        'status': 'complete',
        'cache_hash': cache_hash,
        'np_qubits': np_qubits,
    }

    stats['tocks']['total'] = sum(stats['tocks'].values())
    
    return stats
