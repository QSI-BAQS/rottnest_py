import json
from rottnest.luanti.visualiser_to_luanti import LuantiVisualiser 


vis = json.load(open('visualiser_example.json', 'r'))

luanti = LuantiVisualiser(vis)

for i in range(100):
    luanti.get_layer(i)
