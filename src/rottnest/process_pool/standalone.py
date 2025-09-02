'''
    Standalone execution without a process pool
'''
from rottnest.plugins import executables, architectures 

from rottnest.compute_units.sequencer import Sequencer
from rottnest.compute_units.layout_proxy import LayoutProxy 
from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser

def compile_from_modules(layout):
    '''
        Assumes that all params and module loads have occurred
    '''
    architecture_module = architectures.get_current_architecture()     
    executable = executables.get_current_executable()

    return compile(layout, executable, architecture_module)

def compile(
    layouts,
    executable,
    architecture
    ):

    # Set architecture and ID
    # If single layout, detect and make it a list
    if isinstance(layouts, (list, tuple)):
        layout_ids = list(range(len(layouts)))
    else:
        layout_ids = [0]
        layouts = [layouts]

    worker = architecture.worker()
    composer = architecture.composer(layouts, executable.get_qubits())

    for layout_id, layout in zip(layout_ids, layouts):
        worker.load_layout(layout_id, layout)


    results_composer = composer.results_composer(layouts, executable.get_qubits())

    parser = PyliqtrParser(executable())
    parser.parse()

    seq = Sequencer(*layout_ids)
    it = seq.sequence_pyliqtr(parser)

    # Check that the iterator is not empty 
    try:
        next(it)
    except StopIteration:
        assert False
    it = seq.sequence_pyliqtr(parser)

    for unit_id, compute_unit in enumerate(it):

        # Emulating serialisation 
        # TODO: pass context to composer
        rz_tag_tracker = compute_unit.extract_rz_tracker().to_dict() 
        widget_json = compute_unit.compile_graph_state().json()

        # TODO: total res
        res = worker.execute_graph_state(
            unit_id,
            layout_id,
            widget_json,
            rz_tag_tracker,
        )
        composed_result = composer.compose_result(unit_id, res)
        yield composed_result 

def compile_from_sequences(
    layouts,
    executable,
    architecture
    ):
    # Set architecture and ID
    # If single layout, detect and make it a list
    if isinstance(layouts, (list, tuple)):
        layout_ids = list(range(len(layouts)))
    else:
        layout_ids = [0]
        layouts = [layouts]

    worker = architecture.worker()
    for layout_id, layout in zip(layout_ids, layouts):
        worker.load_layout(layout_id, layout)

    parser = PyliqtrParser(executable())
    parser.parse()

    seq = Sequencer(*layout_ids)
    it = seq.sequence_pyliqtr(parser)

    # Check that the iterator is not empty 
    try:
        next(it)
    except StopIteration:
        assert False
    it = seq.sequence_pyliqtr(parser)

    for unit_id, compute_unit in enumerate(it):

        # Emulating serialisation 
        # TODO: pass context to composer
        rz_tag_tracker = compute_unit.extract_rz_tracker().to_dict() 
        widget_json = compute_unit.compile_graph_state().json()
        # TODO: total res
        res = worker.execute_instruction_sequence(
            unit_id,
            widget_json,
            rz_tag_tracker,
            layout_id,
            False,
        )
        yield res

