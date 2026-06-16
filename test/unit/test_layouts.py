'''
    Layout proxy unit tests
'''
import unittest
import random

from rottnest.compute_units.layout_proxy import LayoutProxy

from rottnest.plugins import architectures
from rottnest.architecture_interface.rottnest_architecture import RottnestArchitecture


def make_dummy_arch(mem_fn):
    class DummyDesigner():
        @staticmethod
        def get_mem_bound(layout):
            return mem_fn(layout)

    class DummyArchitecture(RottnestArchitecture):
        @staticmethod
        def get_name():
            return "DummyArch"

        @staticmethod
        def designer(*a, **ka):
            return DummyDesigner

    return DummyArchitecture



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


    def test_add_layout(self):
        '''
            Sanity check to ensure that add_layout w/out specified
            id does add with distinct ids
        '''
        LayoutProxy.flush()
        layout_vals = {}
        idx = 0
        for _ in range(100):
            layout_vals[idx] = random.randint(100, 1000)
            idx += 1

        for idx, mem in layout_vals.items():
            LayoutProxy.add_layout(
                self.generate_layout_obj(mem)
            )

        self.assertEqual(len(LayoutProxy.saved_layouts), 100)


    def test_layout_architecture_mem_bound(self):
        arch_1 = make_dummy_arch(lambda l: l['mem_bound'])
        arch_2 = make_dummy_arch(lambda l: 2 * l['mem_bound'])

        architectures._force_set_current_architecture(arch_1)

        LayoutProxy.flush()

        LayoutProxy.add_layout_with_id(0, self.generate_layout_obj(10))

        layout = LayoutProxy(0)
        self.assertEqual(layout.num_registers, 10)

        # switch arch and force refresh
        architectures._force_set_current_architecture(arch_2)

        LayoutProxy.force_proxy_refresh()

        self.assertEqual(layout.num_registers, 20)



if __name__ == '__main__':
    unittest.main()
