import numpy as np
import time

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.input_parsers.cirq_parser import CirqParser

from rottnest.executables.fermi_hubbard import make_fh_circuit

N = 2  
fh = make_fh_circuit(N=N,p_algo=0.9999999904,times=0.01)
parser = PyliqtrParser(fh)
parser.parse()

circ_parser = CirqParser(100)

# Create generator object
for circuit in parser.traverse():
    for seq in circ_parser.parse(circuit):
        pass    
        #print(seq)
