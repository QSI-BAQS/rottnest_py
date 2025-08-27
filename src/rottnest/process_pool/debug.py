class DebugComputeUnit:
    unit_id = 'debug'
    
    def __init__(self, obj = None):
        self.obj = obj
    
    def compile_graph_state(self):
        return self
    
    def json(self):
        if self.obj is None:
            return {
                "n_qubits": 4,
                "consumptionschedule": [[{0: []}], [{1: [0]}], [{2: [1]}], [{3: [2]}]],
                "adjacencies": {0: [1], 1: [0], 2: [3], 3: [2]}
            }
        else:
            import json
            return json.load(self.obj)

def _add_dict(d1, d2):
    return {
        k: d1.get(k, 0) + d2.get(k, 0)
        for k in d1.keys() | d2.keys()
    }

def add_result_dicts(res1, res2):
    return {
        'volumes': _add_dict(res1.get('volumes', {}), res2.get('volumes', {})),
        't_source': _add_dict(res1.get('t_source', {}), res2.get('t_source', {})),
        'tocks': _add_dict(res1.get('tocks', {}), res2.get('tocks', {})),
    }

def _iadd_dict(d1, d2):
    for k in d2:
        d1[k] = d1.get(k, 0) + d2[k]

def iadd_result_dicts(res1, res2):
    if 'volumes' not in res1:
        res1['volumes'] = {}
    if 't_source' not in res1:
        res1['t_source'] = {}
    if 'tocks' not in res1:
        res1['tocks'] = {}
    _iadd_dict(res1['volumes'], res2.get('volumes', {}))
    _iadd_dict(res1['t_source'], res2.get('t_source', {}))
    _iadd_dict(res1['tocks'], res2.get('tocks', {}))




