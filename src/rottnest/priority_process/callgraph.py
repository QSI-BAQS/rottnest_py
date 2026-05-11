"""
    Model for Callgraph
"""

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser

from rottnest.plugins import executables

class CallGraph:
    '''
        Singleton instance class for tracking and handling state of the
         callgraph model
        If multiple sessions are required then we can rebind from singleton to
         per-instance models.
    '''

    # Going back should flush the view cache
    view_cache = {}
    hash_cache = {}

    # Pagination
    GRAPH_LIMIT = 100

    curr_executable_id = None

    @classmethod
    def generate_root_node(cls):
        '''
            Generates the root node of the graph
        '''
        executable = executables.get_current_executable()

        parser = PyliqtrParser(executable())
        parser.parse()
        return parser

    @classmethod
    def get_graph(
        cls,
        graph_id: str,
        graph_limit_range=None  # (0, cls.GRAPH_LIMIT)
    ):
        '''
            Gets a pylitrq parser object from a graph_id
        '''
        # executable = executables.get_current_executable()

        # If no ID is passed, then this is a root node
        if graph_id is None:
            prefix = ''
            parser = cls.generate_root_node()
            cls.curr_executable_id = id(executables.get_current_executable())

        # Non-root request
        else:

            # Check that the executable hasn't been changed
            # if cls.curr_executable_id != id(executable):
            #     # TODO View error handling
            #     return None

            # Collect the correct paraser and set up the prefix

            # TODO: Check to see if the graph_id can be used on
            # the view_cache itself
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

            # NOTE: expands was not used until this commit
            #   issue with 
            graph.append(node.to_dict(expands))

        return graph

    @classmethod
    def get_visualiser_parser(cls, graph_id):
        '''
            Gets the visualiser parser
        '''
        graph_node = cls.view_cache.get(graph_id, None)
        if graph_node is None:
            return graph_node
        return graph_node.parser


    @classmethod
    def flush_caches(cls):
        '''
            Reset callgraph caches
            This prevents bad cache entires between state updates on the  
            executable or parameters
        '''
        cls.view_cache = {}
        cls.hash_cache = {}
