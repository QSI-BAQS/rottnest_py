from functools import partial

import numpy as np

import cabaliser.gates as CGates

from pandora.gate_translator import PandoraGateTranslator as PGMap

class PandoraTranslator:
    '''
        Provides a means of mapping pandora gates to their cabaliser equivalents
    '''
    def __init__(self, epsilon=1E-5):

        '''
            Map <gate_id> -> function returning iter<(opcode, (args, ...))> for the matching
            cabaliser operation

            Specifically, each function should have an interface:
            (gate, qubit_labels, rz_tags) -> iter<(opcode, (args, ...))> | None
        '''
        self.pandora_map = {
            # Standard
            PGMap._PauliX.value: self.PauliX,
            PGMap._PauliZ.value: self.PauliZ,
            PGMap._PauliY.value: self.PauliY,
            PGMap.M.value: self.Measure,
            PGMap.CNOT.value: self.CNOT,
            PGMap.CZ.value: self.CZ,

            # Special Cased (may fail)
            PGMap.HPowGate.value: self.HPow,
            PGMap.CZPowGate.value: self.CZPow,
            PGMap.CXPowGate.value: self.CXPow,

            PGMap.Rx.value: self.Rx,
            PGMap.Ry.value: self.Ry,
            PGMap.Rz.value: self.Rz,

            PGMap.XPowGate.value: self.XPow,
            PGMap.YPowGate.value: self.YPow,
            PGMap.ZPowGate.value: self.ZPow,

            # Unimplemented (NO-OP)
            PGMap.In.value: self.no_gate,
            PGMap.Out.value: self.no_gate,
            PGMap.GlobalPhaseGate.value: self.no_gate,
            PGMap.ResetChannel.value: self.no_gate,
            PGMap.GlobalIn.value: self.no_gate,
            PGMap.GlobalOut.value: self.no_gate,

            # Unimplemented (Error)
            PGMap.XXPowGate.value: self.unsupported_gate,
            PGMap.ZZPowGate.value: self.unsupported_gate,
            PGMap.CCXPowGate.value: self.unsupported_gate,
            PGMap.Toffoli.value: self.unsupported_gate,
            PGMap.And.value: self.unsupported_gate,
        }

        self.rotation_table = {
            1.0: self.Z,
            0.5: self.S,
            -0.5: self.SDag,
            -1.0: self.Z,
        }

        self.epsilon = epsilon


    def translate_gate(self, gate, qubit_labels, rz_tags):
        '''
            Translates a single gate to a corresponding cabaliser object
        '''
        return self.pandora_map[gate.type](gate, qubit_labels, rz_tags)


    def translate_widget(self, wid, qubit_labels, rz_tags):
        '''
            Translates a widget (__iter__ -> gates) to an iterator of
            tuples of representations of cabaliser objects
        '''
        translator = lambda g: self.translate_gate(g, qubit_labels, rz_tags)
        return filter(lambda x: x is not None, map(translator, wid))


    def translate_into(self, wid, qubit_labels, rz_tags, opseq):
        '''
            Wrapper for "translate a given widget, adding it to a given operation sequence"
        '''
        for op_group in self.translate_widget(wid, qubit_labels, rz_tags):
            self.add_to_opseq(op_group, opseq)


    def add_to_opseq(self, tl, opseq):
        '''
            Helper method that appends a translation result
            to an operation sequence
        '''
        for op in tl:
            gate, args = op
            opseq.append(gate, *args)


    def get_rotation_gate(self, angle):
        return self.rotation_table.get(angle, self.Rz)


    def no_gate(self, *args, **kwargs):
        '''
            Trivial stand-in for pandora gates that do not map to cabaliser gates
        '''
        return None


    def unsupported_gate(self, gate, *args, **kwargs):
        '''
            Trivial stand-in for pandora gates that are unsupported
        '''
        raise NotImplementedError(f"Gate of id {gate.type}, params ({gate.params}, {gate.global_shift}) is unsupported")


    def single_qubit_gate(self, op, gate, qubit_labels, rz_tags):
        target = qubit_labels.get_single_qubit(gate)
        return (
            (op, (target,)),
        )


    def Rx(self, gate, qubit_labels, rz_tags):
        '''
            Rx = H Rz H
        '''
        target = qubit_labels.get_single_qubit(gate)
        rot = self.get_rotation_gate(gate.param)(gate, qubit_labels, rz_tags)
        h = self.H(gate, qubit_labels, rz_tags)
        return (
            *h,
            *rot
            *h,
        )

    def Ry(self, gate, qubit_labels, rz_tags):
        '''
            Ry = S Rx SDag
        '''
        target = qubit_labels.get_single_qubit(gate)
        rot = self.Rx(gate, qubit_labels, rz_tags)
        s = self.S(gate, qubit_labels, rz_tags)
        sdag = self.SDag(gate, qubit_labels, rz_tags)
        return (
            *s,
            *rot,
            *sdag,
        )

    def Rz(self, gate, qubit_labels, rz_tags):
        target = qubit_labels.get_single_qubit(gate)
        tag = rz_tags.get(gate.param, self.epsilon)
        return (
            (CGates.RZ, (target, tag)),
        )

    def XPow(self, gate, qubit_labels, rz_tags):
        gate.param *= np.pi
        return self.Rx(gate, qubit_labels, rz_tags)

    def YPow(self, gate, qubit_labels, rz_tags):
        gate.param *= np.pi
        return self.Ry(gate, qubit_labels, rz_tags)

    def ZPow(self, gate, qubit_labels, rz_tags):
        gate.param *= np.pi
        return self.Rz(gate, qubit_labels, rz_tags)

    def HPow(self, gate, qubit_labels, rz_tags):
        if gate.param != 1.0:
            return self.unsupported_gate(gate)
        else:
            return self.H(gate, qubit_labels, rz_tags)

    def PauliX(self, gate, qubit_labels, rz_tags):
        return self.single_qubit_gate(CGates.X, gate, qubit_labels, rz_tags)

    def PauliZ(self, gate, qubit_labels, rz_tags):
        return self.single_qubit_gate(CGates.Z, gate, qubit_labels, rz_tags)

    def PauliY(self, gate, qubit_labels, rz_tags):
        return self.single_qubit_gate(CGates.Y, gate, qubit_labels, rz_tags)

    def Measure(self, gate, qubit_labels, rz_tags):
        return self.single_qubit_gate(CGates.MEAS, gate, qubit_labels, rz_tags)

    def CNOT(self, gate, qubit_labels, rz_tags):
        targets = qubit_labels.get_two_qubit(gate)
        return (
            (CGates.CNOT, targets),
        )

    def CZ(self, gate, qubit_labels, rz_tags):
        targets = qubit_labels.get_two_qubit(gate)
        return (
            (CGates.CZ, targets),
        )

    def CZPow(self, gate, qubit_labels, rz_tags):
        # Require exponent 1.0
        if gate.param != 1.0:
            return self.unsupported_gate(gate)
        else:
            return self.CZ(gate, qubit_labels, rz_tags)

    def CXPow(self, gate, qubit_labels, rz_tags):
        # Require exponent 1.0
        if gate.param != 1.0:
            return self.unsupported_gate(gate)
        else:
            return self.CNOT(gate, qubit_labels, rz_tags)

    # Internal rotations from rotation_table
    def H(self, gate, qubit_labels, rz_tags):
        return self.single_qubit_gate(CGates.H, gate, qubit_labels, rz_tags)

    def Z(self, gate, qubit_labels, rz_tags):
        return self.single_qubit_gate(CGates.Z, gate, qubit_labels, rz_tags)

    def S(self, gate, qubit_labels, rz_tags):
        return self.single_qubit_gate(CGates.S, gate, qubit_labels, rz_tags)

    def SDag(self, gate, qubit_labels, rz_tags):
        return self.single_qubit_gate(CGates.SDag, gate, qubit_labels, rz_tags)
