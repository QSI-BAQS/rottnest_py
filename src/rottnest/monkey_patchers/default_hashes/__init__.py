from . import pyliqtr_hashes, cirq_hashes, qualtran_hashes

from functools import reduce

modules = [pyliqtr_hashes, cirq_hashes, qualtran_hashes]
TARGETS = reduce(lambda x, y: x | y.TARGETS, modules, dict()) 
