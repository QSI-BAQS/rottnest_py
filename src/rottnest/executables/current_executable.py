from rottnest.executables import executables 
from functools import partial

from ejc.executable import EJC 
from rottnest_qchem.hydrogen import Hydrogen

from factoring.rottnest_adder import Adder 

current_executable = Adder(n_qubits=4096, window=64, pandora=True) 

#current_executable = Hydrogen(dist=0.2)

#current_executable = executables.FermiHubbard(N=2)

#current_executable = EJC(10, 1, epsilon_target=0.25)
