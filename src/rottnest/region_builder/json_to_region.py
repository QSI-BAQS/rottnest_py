from t_scheduler.templates.generic_templates import LayoutNode 
from t_scheduler.widget.region_types import region_types

def conv(region_type_str, width, height, *args, **kwargs) -> callable:
    return partial(region_types[region_type_str], *args, width=width, height=height, **kwargs)



example = {
height: 20
width: 10
regions:
[
{
    region_type : "CombShapedRegion",
    x: 0,
    y: 0,
    height: 10,
    width: 10,
    downstream: [
    {
        region_type: "RouteBus",
        x: 0,
        y: 10,
        height: 1,
        width: 10,
        downstream: [
            {
                region_type: "BellRegion", 
                x: 0,
                y: 11, 
                height: 9,
                width: 1,
                bell_rate: 1
            }, 
            {
                region_type: "MagicStateFactoryRegion",
                x: 1,
                y: 11, 
                height: 9,
                width: 8,
                factory_type: "cultivator" 
            },
            {
                region_type: "BellRegion", 
                x: 9,
                y: 11, 
                height: 9,
                width: 1,
                bell_rate: 1
            },
        ]
    }
    ]
}
]
}

def json_to_layout(obj):
    """
    :: obj :: Json equivalent dictionary 
    Json should take the form of a tree rooted on the register region   
    """
      
    pass
