from . import adjoint, lcu, mct 

from functools import reduce

modules = [adjoint, lcu, mct]
TARGETS = reduce(lambda x, y: x | y.TARGETS, modules, dict()) 
