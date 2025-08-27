from rottnest.executables import executables 

from functools import partial

from ..plugins.executable_plugins import ExecutablePlugins

executable_manager = ExecutablePlugins()


##from ejc.executable import EJC 
##from rottnest_qchem.hydrogen import Hydrogen
#
##from factoring.rottnest_adder import Adder 
#
#
##current_executable = Adder(n_qubits=64, window=8, pandora=False) 
#
##current_executable = Hydrogen(dist=0.2)
#
#current_executable = executables.FermiHubbard(N=2, pandora=False)
#
##current_executable = EJC(10, 1, epsilon_target=0.25)
#
