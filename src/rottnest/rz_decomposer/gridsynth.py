import os
import numpy as np
import subprocess
from decimal import Decimal
from functools import lru_cache

# Try a self import 
from rottnest.rz_decomposer import rz_decomposer
from rottnest.rz_decomposer import gridsynth

# Default precision in bits

X = object()
Z = object()
Hadamard = object()
Phase = object()
T = object()

class Gridsynth(rz_decomposer.RzDecomposer):
    '''
        Gridsynth management
        Main concern with set-up is setting the default precision 
        TODO: Make sure that if this is invoked by workers that they communicate the required precision
        TODO: Precision should be sourced from the current executable
    '''
    GATE_SYNTH_BNR = os.path.join(os.path.dirname(gridsynth.__file__), 'gridsynth')
    CMD = f"{GATE_SYNTH_BNR}".split() 
  
    DEC_Z = Decimal(1)
    DEC_S = Decimal(0.5)
    DEC_T = Decimal(0.5)

    # TODO: IR  
    DEFAULT_GATE_DICT = {
            'X':X,
            'Z':Z,
            'S':Phase,
            'H':Hadamard,
            'T':T
            }

    def __init__(self, gate_dict=None, default_precision=rz_decomposer.DEFAULT_PRECISION):
        # Because these depend on the location of the file they can't be trusted at compile time
        self.proc = subprocess.Popen(self.CMD, stdin=subprocess.PIPE, stdout=subprocess.PIPE) 
        if gate_dict is None:
            self.gate_dict = self.DEFAULT_GATE_DICT
        else:
            self.gate_dict = gate_dict
        self.precision = None
        self.precision_decimal = None
        self.set_precision(default_precision)

    def set_precision(self, precision):
        '''
            Sets the precision
        '''
        self.precision = precision
        self.precision_decimal = Decimal(2) ** Decimal(-1 * precision)

    def get_precision(self, precision):
        '''
            Gets the current precision
        '''
        return self.precision

    @lru_cache
    def z_theta_instruction(self, p, q, *, precision=None, effort=25, seed=0):
        '''
            Returns a series of gates that perform Z(PI * p / q) with some epsilon precision
        '''
        if precision is None:
            precision = self.precision
  
        approx_angle = Decimal(p) / Decimal(q)
        if abs(approx_angle) % self.DEC_Z < self.precision_decimal: 
            return []

        if abs(self.DEC_S - (approx_angle % self.DEC_Z)) < self.precision_decimal:
            return ['S']

        if abs(self.DEC_T - (approx_angle % self.DEC_S)) < self.precision_decimal:
            return ['T']

        self.proc.stdin.write(f"{p} {q} {precision} {effort} {seed}\n".encode('ascii'))
        self.proc.stdin.flush()
        sequence = self.proc.stdout.readline().decode()
        try:
            op_sequence = sequence.split('[')[1].split(']')[0].split(',')[::-1]
        except:
            return []
        return op_sequence 

    def __del__(self):
        self.proc.terminate()
