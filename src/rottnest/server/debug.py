'''
    
'''

import rottnest.server.controller.arch.lat2d as _archlat2d
import rottnest.server.controller.cg.lat2d as _cglat2d
from rottnest.server.responder import responder

resp = responder


for (k, v) in resp.fullqual_resp_map.items():
    print("'{}'".format(k))
 #   print(v)
