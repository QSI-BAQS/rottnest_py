"""
    View generation elements for the
"""

NODE_NAME = "name"
NODE_DESCRIPTION = "description"
NODE_CHILDREN = "children"
NODE_ID = "id"
NODE_EXPANDS = "expands"

NODE_ROOT = "root_index"
NODE_GRAPH = "graph"

def callgraph_node(
    name: str,
    description: str,
    children: list,
    handle_id: int,
    expands: bool
    ):
    """

        Builds a node for the callgraph
    """
    return {
            NODE_NAME: name,
            NODE_DESCRIPTION: description,
            NODE_CHILDREN: children,
            NODE_ID: handle_id,
            NODE_EXPANDS: expands,
            }

def callgraph_segment(
    handle_id: int,
    graph: list
    ):
    """

Constructs a view for a list of graph nodes
    """
    return {
            NODE_ROOT : handle_id,
            NODE_GRAPH : graph
        }
