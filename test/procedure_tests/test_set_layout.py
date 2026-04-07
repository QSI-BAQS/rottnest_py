'''
    Tests pool process
'''
import unittest

from rottnest.procedures.option_setters.layout_setters import SetLayoutProcedure 
from rottnest.compute_units.layout_proxy import LayoutProxy


class PreprocessorProcedureTest(unittest.TestCase):

    def test_set_layout(self):
        layout = object()
        proc = SetLayoutProcedure(layout)
        proc.execute()

        obj = LayoutProxy.get_layout(0)
        assert obj is layout


if __name__ == '__main__':
    tst = PreprocessorProcedureTest()
    tst.test_set_layout()

    #unittest.main()

