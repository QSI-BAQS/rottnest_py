'''
    Standalone execution without a process pool
'''
from rottnest.plugins import executables, architectures 

from rottnest.compute_units.sequencer import Sequencer
from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser

def compile_from_modules(layout):
    '''
        Assumes that all params and module loads have occurred
    '''
    architecture_module = architectures.get_current_architecture()     
    executable = executables.get_current_executable()

    return compile(layout, executable, architecture_module)

def compile(
    layout,
    executable,
    architecture
    ):

    # Set architecture and ID
    arch_id = 0
                                                                      
    worker = architecture.worker()
    worker.load_architecture(arch_id, layout)
                                                                      
    parser = PyliqtrParser(executable())
    parser.parse()
                                                                      
    seq = Sequencer(arch_id)
    it = seq.sequence_pyliqtr(parser)
                                                                      
    # Check that the iterator is not empty 
    try:
        next(it)
    except StopIteration:
        assert False
                                                                      
    it = seq.sequence_pyliqtr(parser)
                                                                      
    for unit_id, compute_unit in enumerate(it):
                                                                      
        # Emulating serialisation 
        rz_tag_tracker = compute_unit.extract_rz_tracker().to_dict() 
        widget_json = compute_unit.compile_graph_state().json()
                                                                      
        worker.execute_graph_state(
            unit_id,
            widget_json,
            rz_tag_tracker,
            arch_id,
            False,
        )
