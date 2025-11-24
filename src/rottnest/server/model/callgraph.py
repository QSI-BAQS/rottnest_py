"""
    Model for Callgraph
"""

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser

from rottnest.plugins import executables as singleton

from rottnest.server.view import callgraph as view


class CallGraphModel:
    '''
        Singleton instance class for tracking and handling state of the
         callgraph model
        If multiple sessions are required then we can rebind from singleton to
         per-instance models.
    '''

    # Going back should flush the view cache
    view_cache = {}
    hash_cache = {}

    GRAPH_LIMIT = 100

    curr_executable_id = None

    @classmethod
    def generate_root_node(cls):
        '''
            Generates the root node of the graph
        '''
        parser = PyliqtrParser(
            singleton.get_current_executable()
        )
        parser.parse()
        return parser

    @classmethod
    def get_graph(
        cls,
        graph_id: str,
        graph_limit_range: tuple  # (0, cls.GRAPH_LIMIT)
    ):
        '''
            Gets a pylitrq parser object from a graph_id
        '''

        # If no ID is passed, then this is a root node
        if graph_id is None:
            prefix = ''
            parser = cls.generate_root_node()
            cls.curr_executable_id = id(singleton.get_current_executable)

        # Non-root request
        else:

            # Check that the executable hasn't been changed
            if cls.curr_executable_id != id(singleton.get_current_executable):
                # TODO View error handling
                return None

            # Collect the correct paraser and set up the prefix
            prefix = graph_id
            parser = cls.view_cache[graph_id].parser

        # Create a graph view object and a prefix counter
        graph = []
        count = 0

        for node in parser.unroll_graph(prefix=prefix):
            count += 1

            if count > cls.GRAPH_LIMIT:
                break

            handle_id = node.handle_id
            expands = False

            if node.rottnest_hash is not None:
                expands = True
                if (
                    node.name is None
                    or node.rottnest_hash in cls.hash_cache
                   ):  # Cache without name triggers cache load
                    node = cls.hash_cache[node.rottnest_hash]

                else:  # Cache with name triggers cache set
                    # Node triggers cache update
                    cls.hash_cache[node.rottnest_hash] = node
            if node.rottnest_hash is None:
                expands = False

            # Populate the view cache
            cls.view_cache[handle_id] = node

            graph.append(
                view.callgraph_node(
                    node.name,
                    node.description,
                    [],
                    handle_id,
                    expands,
                )
            )
        graph_segment = view.callgraph_segment(0, graph)

        return graph_segment
