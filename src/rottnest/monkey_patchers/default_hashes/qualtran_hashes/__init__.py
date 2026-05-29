from . import adjoint, lcu, mct, on_each

from functools import reduce

modules = [adjoint, lcu, mct, on_each]
TARGETS = reduce(lambda x, y: x | y.TARGETS, modules, dict())
