from qualtran import BloqBuilder


def build_bloq(registers, gates):
    bloq = BloqBuilder()
    reg_map = {}

    for reg in registers:
        reg_map[reg] = bloq.add_register(reg, 1)

    for gate, regs in gates:
        reg_soqs = {}
        for i, r in regs.items():
            reg_soqs[i] = reg_map[r]
        res = bloq.add(gate, **reg_soqs)
        for n, i in enumerate(regs.values()):
            reg_map[i] = res[n]

    return bloq.finalize(**reg_map)
