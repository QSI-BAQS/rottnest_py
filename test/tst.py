from enum import Enum, auto
import multiprocessing as mp
from threading import Thread
from typing import Any
from rottnest.compute_units.compute_unit import ComputeUnit 
from rottnest.compute_units.sequencer import Sequencer
from rottnest.input_parsers.interrupt import INTERRUPT, CACHED
from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
import rottnest.input_parsers.pyliqtr_parser as pyliqtr_parser
import time 
import queue
import select
from copy import deepcopy

from collections import defaultdict, deque

from rottnest.process_pool.process_worker import pool_worker_main
from rottnest.executables.current_executable import current_executable

from rottnest.input_parsers.cirq_parser import shared_rz_tag_tracker
from rottnest.compute_units.architecture_proxy import saved_architectures

test_arch_cmd_obj = {"cmd":"use_arch","payload":{"width":20,"height":20,"regions":[{"region_type":"CombShapedRegisterRegion","x":0,"y":0,"width":20,"height":10,"downstream":[{"region_type":"RouteBus","x":0,"y":10,"width":20,"height":1,"downstream":[{"region_type":"BellRegion.output_region","x":0,"y":11,"width":1,"height":9,"downstream":[],"router_type":"BellRouter","bell_rate":1},{"region_type":"BellRegion.input_region","x":19,"y":11,"width":1,"height":9,"downstream":[],"router_type":"BellRouter","bell_rate":1},{"region_type":"MagicStateBufferRegion","x":1,"y":11,"width":18,"height":2,"downstream":[{"region_type":"RouteBus","x":1,"y":13,"width":18,"height":1,"downstream":[{"region_type":"MagicStateFactoryRegion.with_litinski_6x3_dense","x":1,"y":14,"width":18,"height":6,"downstream":[],"router_type":"MagicStateFactoryRouter","factory_type":"cultivator"}],"router_type":"StandardBusRouter"}],"router_type":"RechargableBufferRouter"}],"router_type":"StandardBusRouter"}],"router_type":"CombRegisterRouter","incl_top":False}]}}
saved_architectures[0] = test_arch_cmd_obj["payload"]




parser = PyliqtrParser(current_executable())
parser.parse()
seq = Sequencer(0)
it = seq.sequence_pyliqtr(parser)
check={CACHED.START: "START", CACHED.END: "END", CACHED.REQUEST: "REQ"}

# First 5 should be SEQUENCE START objs
for _ in range(5):
    obj = next(it)
    print(obj)
    if obj == INTERRUPT:
        print(obj.cache_hash(), check[obj.request_type])

# Trigger debugger on next
import pdb; 
debugger = pdb.Pdb()
debugger.runcall(next, it)

# Next parser object should be the multiand
# obj = next(it) 
# print(obj)
# if obj == INTERRUPT:
#     print(obj.cache_hash(), check[obj.request_type])
# if obj == INTERRUPT and obj.request_type == CACHED.END:
#     raise Exception("Empty!!")
