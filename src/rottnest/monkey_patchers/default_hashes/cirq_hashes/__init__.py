from . import inverse

from functools import reduce

modules = [inverse]
TARGETS = reduce(lambda x, y: x | y.TARGETS, modules, dict()) 
