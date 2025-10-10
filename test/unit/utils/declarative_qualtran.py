from qualtran import BloqBuilder, Bloq, Signature
from qualtran.drawing import show_bloq

'''
def legacy_build_bloq(registers, gates):
    bloqb = BloqBuilder()
    reg_map = {}

    for reg in registers:
        reg_map[reg] = bloqb.add_register(reg, 1)

    for gate, regs in gates:
        reg_soqs = {}
        for i, r in regs.items():
            reg_soqs[i] = reg_map[r]
        res = bloqb.add(gate, **reg_soqs)
        if not isinstance(res, tuple):
            res = (res,)
        for n, i in enumerate(regs.values()):
            reg_map[i] = res[n]

    bloq = bloqb.finalize(**reg_map)
    return bloq
'''


def build_bloq(registers, gates):
    class CustomBloq(Bloq):
        def build_composite_bloq(s, bb, **soqs):
            reg_map = {}
            for reg in registers:
                reg_map[reg] = soqs[reg]

            for gate, regs in gates:
                reg_soqs = {}
                for i, r in regs.items():
                    reg_soqs[i] = reg_map[r]
                res = bb.add(gate, **reg_soqs)
                if not isinstance(res, tuple):
                    res = (res,)
                for n, i in enumerate(regs.values()):
                    reg_map[i] = res[n]

            return reg_map

        @property
        def signature(s):
            return Signature.build(**dict([(n, 1) for n in registers]))

        def __iter__(self):
            # Drop qualtran object down to a cirq circuit
            # This saves having qualtran details in decomp logic
            for cirq_gate in self.decompose_bloq().to_cirq_circuit():
                yield cirq_gate

    return CustomBloq()
