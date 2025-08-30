'''
    Simple architecture stats object
'''

class LayoutStats(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self['num_registers'] = self.get('num_registers', 0)

    def __add__(self, other):
        res = LayoutStats(self)
        for key, val in other.items():
            res[key] = res.get(key, 0) + val
        return res

    @property
    def num_registers(self):
        return self['num_registers']
