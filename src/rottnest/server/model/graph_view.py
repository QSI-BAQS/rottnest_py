from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.executables import current_executable

view_cache = {}

def get_graph():
    pyliqtr_obj = current_executable.current_executable 

    parser = PyliqtrParser(pyliqtr_obj) 
    parser.parse()

    graph = []


    # TODO: move the view logic to view
    for node in parser.unroll_graph():

        # Populate the view cache
        view_cache[node.handle_id] = node

        graph.append(
        {
            "name": node.name, 
            "description": node.description, 
            "children": [],
            "id": node.handle_id
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


