from rottnest.executables import executables 
from functools import partial

from ejc.executable import EJC 
#current_executable = executables.FermiHubbard(N=20)

current_executable = EJC(10, 1, epsilon_target=0.25)
