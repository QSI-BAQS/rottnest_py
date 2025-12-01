from qualtran import BloqBuilder, Bloq, Signature


def build_bloq(registers, gates):
    '''
        Declaratively creates a new Qualtran Bloq

        IN:
            registers [Collection<str>]
                A collection of named registers

            gates [Collection<Tuple(Bloq, Dict<str><str>)>]
                A collection of pairs (<Bloq>, <QubitRegs>), where <QubitRegs> maps
                from the input argument names expected for the <Bloq> to the associated
                regsiter
                Handled in sequence


        OUT: [CustomBloq]
                A new Bloq (of a custom internal class) that implements a Signature
                and a CompositeBloq builder for decomposition

        eg.
        ```
        build_bloq(
            registers = ('x', 'y'),
            gates = [
                (qualtran.bloqs.basic_gates.CNOT(), {'ctrl': 'x', 'target': 'y'})
            ]
        )
        ```
        creates a Bloq that describes a circuit that consists of a single CNOT over two qubits.
        `'ctrl'` and `'targ'` are taken from the Signature/args for a qualtran CNOT.
    '''
    class CustomBloq(Bloq):
        def build_composite_bloq(s, bb, **soqs):
            # Load named registers to be tracked
            reg_map = {}
            for reg in registers:
                reg_map[reg] = soqs[reg]

            # For (gate, regs) pairs, create the corresponding gate
            # over those registers
            for gate, regs in gates:
                # Fetch the required soquets from the tracker
                reg_soqs = {}
                for i, r in regs.items():
                    reg_soqs[i] = reg_map[r]

                # Add the gate to the bloqbuilder
                res = bb.add(gate, **reg_soqs)
                if not isinstance(res, tuple):
                    res = (res,)
                # Extract the corresponding bloqs from the resulting gate back into the map
                # (update the soq references to their latest versions)
                for n, i in enumerate(regs.values()):
                    reg_map[i] = res[n]

            return reg_map

        @property
        def signature(s):
            return Signature.build(**dict([(n, 1) for n in registers]))


    return CustomBloq()
