

def get_gates_by_id(connection, ids: list[int]) -> list[PandoraGate]:
    '''
        Get gates by ID from pandora
    '''
    pandora_gates: list[PandoraGate] = []
    for gid in ids:
        if gid == GLOBAL_IN_ID:
            pandora_gates.append(PandoraGate(gate_id=gid,
                                             gate_code=PandoraGateTranslator.GlobalIn.value))
            continue
        if gid == GLOBAL_OUT_ID:
            pandora_gates.append(PandoraGate(gate_id=gid,
                                             gate_code=PandoraGateTranslator.GlobalOut.value))
            continue

    cursor = connection.cursor()
    sql_statement = ("select * from linked_circuit where id in " + str(tuple(ids)))
    cursor.execute(sql_statement)
    gate_tuples = cursor.fetchall()

    pandora_gates += [PandoraGate(*gate_tuple) for gate_tuple in gate_tuples]

    return pandora_gates
