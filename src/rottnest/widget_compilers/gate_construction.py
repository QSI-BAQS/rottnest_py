from __future__ import annotations
from typing import List
from t_scheduler.base.gate import *
from t_scheduler.base.util import dag_create
from rottnest.input_parsers.rz_tag_tracker import RzTagTracker
from rottnest.gridsynth.gridsynth import Gridsynth


class NopGate():
    pass # TODO !important
gate_map = {
    'T':T_Gate
}


class PseudoRZGate:
    targ: int
    pre: List[PseudoRZGate]
    post: List[PseudoRZGate]
    actual: List[BaseGate]


    def __init__(self, targ, rz_tag):
        self.targ = targ
        self.pre = []
        self.post = []
        self.actual = []
        self.rz_tag = rz_tag

    def unroll(self, gridsynth: Gridsynth, rz_tag_tracker: RzTagTracker):
        if self.rz_tag == 0:
            self.actual = NopGate(self.targ)
            return # Ignore tag 0

        params = rz_tag_tracker.get_gridsynth_params(self.rz_tag)
        instructions = gridsynth.z_theta_instruction(*params)
        # Ignore global phase
        for inst_code in instructions:
            if inst_code in gate_map:
                self.actual.append(gate_map[inst_code](self.targ))

    def prune_unused(self):
        self.pre = [gate for gate in self.pre if gate.actual]
        self.post = [gate for gate in self.post if gate.actual]


    def update_dependencies(self):
        for i in range(len(self.actual)):
            self.actual[i].post = [self.actual[i+1]]
            self.actual[i+1].pre = [self.actual[i]]
        
        self.actual[0].pre = [pre.actual[-1] for pre in self.pre]
        self.actual[-1].post = [post.actual[0] for post in self.post]
    


def make_pseudo_gates(obj, gridsynth, rz_tag_tracker):
    qubit_tag_pairs = [(q, obj['measurement_tags'][q]) for q in range(obj["n_qubits"])]
    gates = [PseudoRZGate(q, tag) for q, tag in qubit_tag_pairs]
    for g in gates:
        g.unroll(gridsynth, rz_tag_tracker)

    dag_layers, _ = dag_create(obj, gates)

    for g in gates:
        g.prune_unused()
    
    for g in gates:
        g.update_dependencies()
    
    return dag_layers