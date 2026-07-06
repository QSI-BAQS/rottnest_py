'''
    Handlers for qualtran functions
'''
from functools import partial

import qualtran
#import qualtran.bookkeeping

from cirq.protocols.circuit_diagram_info_protocol import CircuitDiagramInfoArgs

def get_register_names(gate: "GateOperation | QualtranGate") -> tuple[list, list]:
    '''
        Returns input and output symbols from a gate
        The gate is expected to have been generated from qualtran, and
         hence to contain a signature object under gate.gate.signature
        The qualtran gate matches the signature, the cirq gate matches the symbols
        This works under the assumption of the same order of gate labels in the cirq
         circuit, and that the qualtran gate maps all qubits in the circuit

        Returns a list of input and a list of output register names
        This function has no known side effects
    '''
    # we can get cirq objects here if they're cached :(
    # (eg. pyLIQTR QSP_Prepare)
    if not hasattr(gate.gate, "signature"):
        # cirq style as below
        return gate.qubits, gate.qubits

    sig = gate.gate.signature
    diagram_info = gate._circuit_diagram_info_(CircuitDiagramInfoArgs.UNINFORMED_DEFAULT)
    # technically, we should use the circuit_diagram_info protocol method
    # instead just catch the NotImplementedType
    if diagram_info is NotImplemented:
        # fall back to cirq style "everything is in/out"
        return gate.qubits, gate.qubits
    gate_labels = diagram_info.wire_symbols
    qubit_labels = gate.qubits

    input_sigs = {s.name for s in sig.lefts()}
    output_sigs = {s.name for s in sig.rights()}

    inputs = []
    outputs = []

    # Strcmp on the gate args to match to the signature
    # THRU implies both input and output
    for sig_match, circ_match in zip(gate_labels, qubit_labels):
        if sig_match in input_sigs:
            inputs.append(circ_match)

        if sig_match in output_sigs:
            outputs.append(circ_match)

    # TEMP : worst case is cirq style is something goes wrong w/ string matching
    non_io = set(gate.qubits).difference(inputs).difference(outputs)
    if non_io:
        # print(f"Non-I/O for {gate.gate} - {gate.gate.signature}:\n{gate_labels}\n{non_io}")
        return gate.qubits, gate.qubits

    return inputs, outputs

def arbitrary_clifford():
    '''
        Worst case N qubit clifford
    '''
    def _wrap(
        self,
        operation_sequence: OperationSequence,
        qubit_labels: QubitLabelTracker,
        rz_tags: QubitLabelTracker):

        # Replace this with an n qubit arb cliff
        for i in range(0, self.n, 2):
            operation_sequence.append(
                cabaliser.gates.CNOT,
                (0, 1) # Get targets
            )

def blank():
    def _wrap():
        pass
    return _wrap

#qualtran_ops = {
#    bookkeeping.join.Join: blank,
#    bookkeeping.split.Split: blank,
#    bookkeeping.arbitrary_clifford.ArbitraryClifford: arbitrary_clifford
#}
