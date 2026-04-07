'''
This module contains a set of Monkey Patchers for pyliqtr
These methods extend pyliqtr objects with hooks for rottnest and cabaliser

The monkey patches run on import, and should be treated with caution.  
All callable patches are promoted to MethodTypes objects. 

'''
from . import qualtran_patcher, cirq_patcher, pyliqtr_patcher
from . decomposition_targets import get_hash_patcher, load_hash_patcher, clear_hash_patcher
from . decomposition_targets import add_cirq_hash, add_qualtran_hash, add_pyliqtr_hash, get_tracking_targets

