from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.executables import current_executable
from rottnest.input_parsers.interrupt import INTERRUPT, CACHED
#from rottnest.pandora.pandora_sequencer import PandoraSequencer

# TODO:
# Going back should flush the view cache
view_cache = {}
hash_cache = {}

GRAPH_LIMIT = 100

def get_graph(graph_id=None):
   
    if graph_id is None:
        prefix = ''
        parser = PyliqtrParser(current_executable.current_executable())
        parser.parse()
    else:
        prefix = graph_id
        parser = view_cache[graph_id].parser 

    graph = []

    count = 0

    # TODO: move the view logic to view
    for node in parser.unroll_graph(prefix=prefix):
        count += 1
        if count > GRAPH_LIMIT: break
        handle_id = node.handle_id
        expands = False

        if node.rottnest_hash is not None:
            expands = True
            if node.name is None or node.rottnest_hash in hash_cache: # Cache without name triggers cache load  
                node = hash_cache[node.rottnest_hash]

            else: # Cache with name triggers cache set
                # Node triggers cache update
                hash_cache[node.rottnest_hash] = node 
        if node.rottnest_hash is None:
            expands = False
        # Populate the view cache
        view_cache[handle_id] = node

        graph.append(
        {
            "name": node.name, 
            "description": node.description, 
            "children": [],
            "id": handle_id,
            "expands": expands,
        }
            ) 
    graph_segment = {
        "root_index": 0,
        "graph": graph
    }
    return graph_segment 


def get_view(unit_id): 
    '''
        Gets a view of the object
    '''
    if unit_id not in view_cache:
        raise Exception("Unknown ID")
