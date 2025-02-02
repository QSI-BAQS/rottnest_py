from functools import partial
import cabaliser.gates as cabaliser_gates
import pandora
from cabaliser.operation_sequence import OperationSequence

from rottnest.pandora.pandora_qubit_label_tracker import PandoraQubitLabelTracker

def pandora_gates_to_compute_unit(pandora_gates):
    '''
        Enumerates a pandora gate object
    '''
    pass


class PandoraTranslator:
    '''
        Translates pandora gates to cabaliser sequences
    '''
    def __init__(self):
        self.pandora_map = {
            0:  self.In,
            1:  self.Out,
            2:  self.Rx,
            3:  self.Ry,
            4:  self.Rz,
            5:  self.XPowGate,
            6:  self.YPowGate,
            7:  self.ZPowGate,
            8:  self.HPowGate,
            9:  partial(self.single_qubit_gate, cabaliser_gates.X),
            10:  partial(self.single_qubit_gate, cabaliser_gates.Z),
            11:  partial(self.single_qubit_gate, cabaliser_gates.Y),
            12:  self.GlobalPhaseGate,
            13:  self.ResetChannel,
            14:  partial(self.single_qubit_gate, cabaliser_gates.MEAS),
            15:  partial(self.two_qubit_gate, cabaliser_gates.CZ),
            16:  partial(self.two_qubit_gate, cabaliser_gates.CNOT),
            17:  self.CZPowGate,
            18:  self.CXPowGate,
            19:  self.XXPowGate,
            20:  self.ZZPowGate,
            21:  self.Toffoli,
            22:  self.And,
            23:  self.CCXPowGate,
            24:  self.GlobalIn,
            25:  self.GlobalOut
        }
        self.op_map = {
            0: 0,  # self.In,
            1: 0,  # self.Out,
            2: 3,  # self.Rx,
            3: 5,  # self.Ry,
            4: 1,  # self.Rz,
            5: 3,  # self.XPowGate,
            6: 5,  # self.YPowGate,
            7: 1,  # self.ZPowGate,
            8: 1,  # self.HPowGate,
            9: 1,  # self._PauliX,
            10: 1,  # self._PauliZ,
            11: 1,  # self._PauliY,
            12: 0,  # self.GlobalPhaseGate,
            13: 0,  # self.ResetChannel,
            14: 1,  # self.M,
            15: 1,  # self.CNOT,
            16: 1,  # self.CZ,
            17: None,  # self.CZPowGate,
            18: None,  # self.CXPowGate,
            19: 0,  # self.XXPowGate,
            20: 0,  # self.ZZPowGate,
            21: 0,  # self.Toffoli,
            22: 0,  # self.And,
            23: 0,  # self.CCXPowGate,
            24: 0,  # self.GlobalIn,
            25: 0,  # self.GlobalOut
        }
        self.rotation_table = { 
            1.0: self._Z,
            0.5: self._S,
            -0.5: self._Sdag,
            -1.0: self._Z 
        }


    def __call__(self, *args, **kwargs):
        return self.translate(*args, **kwargs)

    def get_rot_gate(self, angle):
        self.rotation_table.get(angle, self._rz)

    def translate(self, pandora_gate, operation_sequence, qubit_labels, rz_tags):
        self.pandora_map[pandora_gate.type](pandora_gate, operation_sequence, qubit_labels, rz_tags) 

    def translate_batch(self, pandora_gates, operation_sequence, qubit_labels, rz_tags):
        '''
            Bulk dispatch call for translate
            Saves passing some parameters around repeatedly
        '''
        for i in pandora_gates:
            self.translate(i, operation_sequence, qubit_labels, rz_tags)

    def rotation_gate(self, gate, operation_sequence, qubit_labels, rz_tags):
        '''
            Wrapper for gates that potentially reduce
        '''
        self.rotation_table.get(gate.param, self._rz)(gate, operation_sequence, qubit_labels, rz_tags)

    def Z_to_X(self, fn, gate, operation_sequence, qubit_labels, rz_tags): 
        '''
        '''
        self._H(gate, operation_sequence, qubit_labels, rz_tags)
        fn(gate, operation_sequence, qubit_labels, rz_tags)
        self._H(gate, operation_sequence, qubit_labels, rz_tags)

    def Z_to_Y(self, fn, gate, operation_sequence, qubit_labels, rz_tags): 
        self._H(gate, operation_sequence, qubit_labels, rz_tags)
        self._S(gate, operation_sequence, qubit_labels, rz_tags)
        fn(gate, operation_sequence, qubit_labels, rz_tags)
        self._Sdag(gate, operation_sequence, qubit_labels, rz_tags)
        self._H(gate, operation_sequence, qubit_labels, rz_tags)

    '''
        These gates are hard coded for ease of reference
    '''
    def _Z(self, gate, operation_sequence, qubit_labels, rz_tags):
        target = qubit_labels.get_single_qubit(gate)
        operation_sequence.append(
            cabaliser_gates.Z,
            target
        )

    def _S(self, gate, operation_sequence, qubit_labels, rz_tags):
        target = qubit_labels.get_single_qubit(gate)
        operation_sequence.append(
            cabaliser_gates.S,
            target
        )

    def _H(self, gate, operation_sequence, qubit_labels, rz_tags):
        target = qubit_labels.get_single_qubit(gate)
        operation_sequence.append(
            cabaliser_gates.H,
            target
        )



    def _Sdag(self, gate, operation_sequence, qubit_labels, rz_tags):
        target = qubit_labels.get_single_qubit(gate)
        operation_sequence.append(
            cabaliser_gates.Sdag,
            target
        )

    def _rz(self, gate, operation_sequence, qubit_labels, rz_tags):
        tag = rz_tags(gate.param)
        operation_sequence.append(
            cabaliser_gates.RZ,
            (target, tag)
        )


    def single_qubit_gate(self, cabaliser_op, gate, operation_sequence, qubit_labels, rz_tags): 
        target = qubit_labels.get_single_qubit(gate)
        operation_sequence.append(
            cabaliser_op,
            target
        )

    def two_qubit_gate(self, cabaliser_op, gate, operation_sequence, qubit_labels, rz_tags): 
        targets = qubit_labels.get_two_qubit(gate)
        operation_sequence.append(
            cabaliser_op,
            *targets
        )


    def NOT_IMPLEMENTED(self, *args, **kwargs):
        raise NotImplementedError 

    def In(self, gate, operation_sequence, qubit_labels, rz_tags):
        # TODO Track qubit indicies from here 
        return 

    def Out(self, gate, operation_sequence, qubit_labels, rz_tags):
        return 


    def Rx(self, gate, operation_sequence, qubit_labels, rz_tags):
        angle = gate.param
        target = qubit_labels.get_single_qubit(gate)

        operation_sequence.append(
            cabaliser_gates.H,
            target
        )
        
        self.get_rotation_gate(angle)

        operation_sequence.append(
            cabaliser_gates.H,
            target
        )



    
    def Ry(self, gate, operation_sequence, qubit_labels, rz_tags):
        pass

    def Rz(self, gate, operation_sequence, qubit_labels, rz_tags):
        pass

    def XPowGate(self, gate, operation_sequence, qubit_labels, rz_tags):
        pass

    def YPowGate(self, gate, operation_sequence, qubit_labels, rz_tags):
        pass

    def ZPowGate(self, gate, operation_sequence, qubit_labels, rz_tags):
        pass

    def HPowGate(self, gate, operation_sequence, qubit_labels, rz_tags):
        pass

    def GlobalPhaseGate(self, gate, operation_sequence, qubit_labels, rz_tags):
        pass

    def ResetChannel(self, gate, operation_sequence, qubit_labels, rz_tags):
        pass

    def M(self, gate, operation_sequence, qubit_labels, rz_tags):
        pass

    def CNOT(self, gate, operation_sequence, qubit_labels, rz_tags):
        targets = qubit_labels.gets(*self.qubits)

        operation_sequence.append(
            cabaliser_gates.CNOT,
            *targets 
        )

    def CZ(self, gate, operation_sequence, qubit_labels, rz_tags):
        targets = qubit_labels.gets(*self.qubits)

        operation_sequence.append(
            cabaliser_gates.CZ,
            *targets 
        )

    def CZPowGate(self, gate, operation_sequence, qubit_labels, rz_tags):
        pass

    def CXPowGate(self, gate, operation_sequence, qubit_labels, rz_tags):
        pass

    def XXPowGate(self, gate, operation_sequence, qubit_labels, rz_tags):
        return self.NOT_IMPLEMENTED() 

    def ZZPowGate(self, gate, operation_sequence, qubit_labels, rz_tags):
        return self.NOT_IMPLEMENTED() 

    def Toffoli(self, gate, operation_sequence, qubit_labels, rz_tags):
        return self.NOT_IMPLEMENTED() 

    def And(self, gate, operation_sequence, qubit_labels, rz_tags):
        return self.NOT_IMPLEMENTED() 

    def CCXPowGate(self, gate, operation_sequence, qubit_labels, rz_tags):
       return self.NOT_IMPLEMENTED() 

    def GlobalIn(self, gate, operation_sequence, qubit_labels, rz_tags):
        pass

    def GlobalOut(self, gate, operation_sequence, qubit_labels, rz_tags):
        pass
