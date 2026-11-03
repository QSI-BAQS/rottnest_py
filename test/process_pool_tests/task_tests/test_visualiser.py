'''
    Tests process pool execution
'''
import time

import unittest

# These workers have been tested without the pool elsewhere

from rottnest.process_pool.singleton import get_pool
from rottnest.process_pool.pool_status import PoolStatus


from rottnest.test_utils.plugin_setup import setup_plugins_decorator
from rottnest.test_utils.layout_setup import setup_layout 

from rottnest_preprocessor.preprocessor import strings


class VisualiserTests(unittest.TestCase):
    '''
        Process pool tests
    '''

    @setup_layout
    @setup_plugins_decorator()
    def test_get_root(self):
        '''
            Tests ping workers through ipc
        '''
        pool = get_pool()
        pool.start()
        pool.synchronise()

        curr_node = None 
        expands = True

        while expands:
            pool.get_callgraph(curr_node)

            # Wait for the pool to emit a callgraph
            while None is (
                    resp := pool.get_callgraph_status()
                ):
                pass
            _, nodes = resp 
            if len(nodes) == 0:
                raise Exception("Decomposition Failed")

            for node in nodes:
                # Found a visualisable node
                if node['expands'] == False:
                    expands = False
                    curr_node = node['handle_id']
            
            # Recursively expand next node
            if expands == True: 
                curr_node = node[0]['handle_id']

        pool.get_visualiser(curr_node)

        # Wait for the pool to emit a visualiser object 
        while None is (
                resp := pool.get_visualiser_status()
            ):
            pass
       
        _, vis_obj = resp 
        assert vis_obj == strings.no_visualiser
         

        pool.terminate()

        
if __name__ == '__main__':
    tst = VisualiserTests()
    tst.test_get_root()
