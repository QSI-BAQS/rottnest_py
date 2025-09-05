'''
    Standalone execution without a process pool
'''
from rottnest.input_parsers.interrupt import INTERRUPT, CACHED
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
    worker.set_precision(executable.get_rz_precision())

    parser = PyliqtrParser(executable())

    seq = Sequencer(*layout_ids, composer=composer)

    parser.parse()

    it = seq.sequence_pyliqtr(parser)

    for obj in it: 
        if obj == INTERRUPT:
            process_elem_cache(obj, composer)
        else:
            process_elem_obj(obj, worker, composer)

    return composer.get_result()


def process_elem_cache(
    cache_obj,
    composer
):
    '''
        Sends control signals to the composer
    '''

    # Process cache command
    if cache_obj.request_type == CACHED.START:
        composer.cache_entry_start(cache_obj)

    elif cache_obj.request_type == CACHED.END:
         composer.cache_entry_end(cache_obj)

    elif cache_obj.request_type == CACHED.REQUEST:

        # For single proc we have a guarantee
        # That non-recursive cache obj are finished
        # Before calling
         composer.cache_request(cache_obj)

def process_elem_obj(
    compute_unit,
    worker,
    composer
):
    '''
        Triggers a compilation
    '''

    # Emulating serialisation 
    rz_tag_tracker = compute_unit.extract_rz_tracker().to_dict() 
    widget_json = compute_unit.compile_graph_state().json()

    # Register compute unit with composer
    composer.submit(compute_unit)

    res = worker.execute_graph_state(
        compute_unit.unit_id,
        compute_unit.layout_id,
        widget_json,
        rz_tag_tracker,
    )

    # Unregister
    # This makes more sense when using the process pool
    composer.receive(
        compute_unit.unit_id,
        res
    )

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

    seq = Sequencer(*layout_ids)
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
