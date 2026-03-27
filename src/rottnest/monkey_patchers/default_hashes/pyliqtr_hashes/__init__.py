from . import pauli_lcu, qsp, qsvt, qubitized_operations 

from functools import reduce

modules = [pauli_lcu, qsp, qsvt, qubitized_operations]
TARGETS = reduce(lambda x, y: x | y.TARGETS, modules, dict()) 
