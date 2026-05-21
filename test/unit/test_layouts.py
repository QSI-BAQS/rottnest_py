'''
    Layout proxy unit tests
'''
import unittest
import random

from rottnest.compute_units.layout_proxy import LayoutProxy


class LayoutProxyTests(unittest.TestCase):

    def generate_layout_obj(self, memory_bound=1000):
        '''
            Generates a simple proxy layout object
        '''
        layout = {'mem_bound': memory_bound}
        return layout

    def test_load_and_store(self):
        '''
            Tests simple load and store functions
        '''

        layout_vals = {}
        idx = 0
        for _ in range(100):
            layout_vals[idx] = random.randint(100, 1000)
            idx += 1

        for idx, mem in layout_vals.items():
            LayoutProxy.add_layout_with_id(
                idx,
                self.generate_layout_obj(mem)
            )

        for idx, mem in layout_vals.items():
            layout = LayoutProxy.get_layout(idx)
            assert mem == layout['mem_bound']

    def test_flush(self):
        '''
            Simple test for flushing and reloading
        '''
        layout_vals = {}
        idx = 0
        for _ in range(100):
            layout_vals[idx] = random.randint(100, 1000)
            idx += 1

        for idx, mem in layout_vals.items():
            LayoutProxy.add_layout_with_id(
                idx,
                self.generate_layout_obj(mem)
            )

        layouts = LayoutProxy.flush()
        assert len(LayoutProxy.saved_layouts) == 0

        LayoutProxy.reload_layouts(layouts)

        for idx, mem in layout_vals.items():
            layout = LayoutProxy.get_layout(idx)
            assert mem == layout['mem_bound']


if __name__ == '__main__':
    unittest.main()
