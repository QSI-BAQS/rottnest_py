'''
    Test helper for setting layouts

'''
from rottnest.compute_units.layout_proxy import LayoutProxy


def setup_layout(*args, layout=None, layout_id = None):
    if len(args) > 0:
        fn = args[0]
        # fn set, this is a bare
        # decorator
        def _wrap(*args, **kwargs):
            _setup_layout()
            return fn(*args, **kwargs)
        return _wrap

    # Not a decorator
    return _setup_layout


def _setup_layout(layout = None, layout_id = None):
    if layout_id is None:
        layout_id = 0
    if layout is None:
        memory_bound = 1000
        layout = {'mem_bound': memory_bound}
    LayoutProxy.add_layout_with_id(layout_id, layout)

