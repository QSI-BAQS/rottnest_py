from t_scheduler.router import *
from t_scheduler.templates.generic_templates import LayoutNode 
from t_scheduler.widget.region_types import region_types

from functools import partial

region_type_map = {}
for mapping in region_types.values():
    region_type_map |= mapping

def conv(region_type, width, height, **kwargs) -> callable:
    if 'downstream' in kwargs:
        kwargs = {k: v for k, v in kwargs.values() if k != 'downstream'}
    return partial(region_type_map[region_type], width=width, height=height, **kwargs)


# TODO move into settings and frontend
default_router = {
    'CombShapedRegisterRegion': CombRegisterRouter,
    'RouteBus': StandardBusRouter,
    'TCultivatorBufferRegion.with_dense_layout': DenseTCultivatorBufferRouter,
    'MagicStateFactoryRegion': MagicStateFactoryRouter,
    'MagicStateFactoryRegion.with_litinski_6x3_dense': MagicStateFactoryRouter,
    'MagicStateBufferRegion': RechargableBufferRouter,
    'SingleRowRegisterRegion': BaselineRegisterRouter,
    'PrefilledMagicStateRegion': VerticalFilledBufferRouter,
    'BellRegion': BellRouter
}



example = {
"height": 20,
"width": 10,
"regions":
[
{
    "region_type": "CombShapedRegisterRegion",
    "x": 0,
    "y": 0,
    "height": 10,
    "width": 10,
    "incl_top": 0,
    "downstream": [
    {
        "region_type": "RouteBus",
        "x": 0,
        "y": 10,
        "height": 1,
        "width": 10,
        "downstream": [
            {
                "region_type": "BellRegion", 
                "x": 0,
                "y": 11, 
                "height": 9,
                "width": 1,
                "bell_rate": 1
            }, 
            {
                "region_type": "TCultivatorBufferRegion",
                "x": 1,
                "y": 11, 
                "height": 9,
                "width": 8,
            },
            {
                "region_type": "BellRegion", 
                "x": 9,
                "y": 11, 
                "height": 9,
                "width": 1,
                "bell_rate": 1
            },
        ]
    }
    ]
}
]
}

def _json_to_node(obj):
    downstream = [_json_to_node(child) for child in obj.pop("downstream", [])]
    return LayoutNode(
        region_factory = conv(**obj),
        router_factory = default_router[obj['region_type']],
        downstream = downstream
    )


def json_to_layout(obj):
    """
    :: obj :: Json equivalent dictionary 
    Json should take the form of a tree rooted on the register region   
    """
    layout = _json_to_node(obj['regions'][0]) # TODO multi-root -> Insert dummy register region as layout root

    return layout
