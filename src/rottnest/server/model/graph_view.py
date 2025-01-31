from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.executables import current_executable
from rottnest.input_parsers.interrupt import INTERRUPT, CACHED

# TODO:
# Going back should flush the view cache
view_cache = {}
hash_cache = {}

def get_graph(graph_id=None):
   
    if graph_id is None:
        prefix = ''
        pyliqtr_obj = current_executable.current_executable() 
    else:
        prefix = graph_id
        pyliqtr_obj = view_cache[graph_id].parser 

    parser = PyliqtrParser(pyliqtr_obj) 
    parser.parse()

    graph = []

    # TODO: move the view logic to view
    for node in parser.unroll_graph(prefix=prefix):

        handle_id = node.handle_id
        expands = False

        if node.rottnest_hash is not None:
            expands = True
            if node.name is None or node.rottnest_hash in hash_cache: # Cache without name triggers cache load  
                node = hash_cache[node.rottnest_hash]

            else: # Cache with name triggers cache set
                # Node triggers cache update
                hash_cache[node.rottnest_hash] = node 
            
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
