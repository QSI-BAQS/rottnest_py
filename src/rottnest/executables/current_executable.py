from rottnest.executables import fermi_hubbard
from functools import partial

current_executable = partial(fermi_hubbard.make_fh_circuit, N=10)
