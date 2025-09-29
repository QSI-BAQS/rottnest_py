import os
import subprocess
from functools import lru_cache

# Try a self import 
from rottnest.gridsynth import gridsynth

X = object()
Z = object()
Hadamard = object()
Phase = object()
T = object()

from rottnest.rz_decomposer.gridsynth import Gridsynth
from rottnest.rz_decomposer.rz_decomposer import DEFAULT_PRECISION

class Gridsynth:
    GATE_SYNTH_BNR = os.path.join(os.path.dirname(gridsynth.__file__), 'gridsynth')
    CMD = f"{GATE_SYNTH_BNR}".split() 
  
    # TODO: IR  
    DEFAULT_GATE_DICT = {
            'X':X,
            'Z':Z,
            'S':Phase,
            'H':Hadamard,
            'T':T
            }

    proc = None

    def __init__(self, gate_dict=None):
        # Because these depend on the location of the file they can't be trusted at compile time
        self.proc = subprocess.Popen(self.CMD, stdin=subprocess.PIPE, stdout=subprocess.PIPE) 
        if gate_dict is None:
            self.gate_dict = self.DEFAULT_GATE_DICT
        else:
            self.gate_dict = gate_dict

    @lru_cache
    def z_theta_instruction(self, p, q, precision=DEFAULT_PRECISION, effort=25, seed=0, **gates):
        '''
            Returns a series of gates that perform Z(PI * p / q) with some epsilon precision
        '''
        print("DECOMP: ", precision, file=open("OUT_gs", 'a'))
        self.proc.stdin.write(f"{p} {q} {precision} {effort} {seed}\n".encode('ascii'))
        self.proc.stdin.flush()
        sequence = self.proc.stdout.readline().decode()
        op_sequence = sequence.split('[')[1].split(']')[0].split(',')[::-1]
        return op_sequence 

    def __del__(self):
        if self.proc is not None:
            self.proc.terminate()

#class Gridsynth:
#    GATE_SYNTH_BNR = os.path.join(os.path.dirname(gridsynth.__file__), 'gridsynth')
#    CMD = f"{GATE_SYNTH_BNR}".split() 
#  
#    # TODO: IR  
#    DEFAULT_GATE_DICT = {
#            'X':X,
#            'Z':Z,
#            'S':Phase,
#            'H':Hadamard,
#            'T':T
#            }
#
#    proc = None
#
#    def __init__(self, gate_dict=None):
#        # Because these depend on the location of the file they can't be trusted at compile time
#        self.proc = subprocess.Popen(self.CMD, stdin=subprocess.PIPE, stdout=subprocess.PIPE) 
#        if gate_dict is None:
#            self.gate_dict = self.DEFAULT_GATE_DICT
#        else:
#            self.gate_dict = gate_dict
#
#    @lru_cache
#    def z_theta_instruction(self, p, q, precision=DEFAULT_PRECISION, effort=25, seed=0, **gates):
#        '''
#            Returns a series of gates that perform Z(PI * p / q) with some epsilon precision
#        '''
#        p = abs(p)
#        self.proc.stdin.write(f"{p} {q} {precision} {effort} {seed}\n".encode('ascii'))
#        self.proc.stdin.flush()
#        sequence = self.proc.stdout.readline().decode()
#        op_sequence = sequence.split('[')[1].split(']')[0].split(',')[::-1]
#
#        print(f"p: {p} q: {q} prec: {precision} gate len: {len(op_sequence)}", file=open("rz_ops", "a"))
#        return op_sequence 
#
#    def __del__(self):
#        if self.proc is not None:
#            self.proc.terminate()
