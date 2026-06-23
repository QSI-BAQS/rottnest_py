'''
    Graph wrapper object
    Wraps a recursive parser
'''

class GraphWrapper:
    '''
        Thin graph node wrapper object
    '''
    def __init__(self, handle_id, name, description="", parser=None, rottnest_hash=None):
        self.handle_id = handle_id
        self.rottnest_hash = rottnest_hash

        self.name = name
        self.description = description
        self.parser = parser

    def get_graph(self):
        '''
            Gets the parser object
        '''
        return self.parser

    def to_dict(self,expands=False):
        '''
           Generates a dictionary object
        '''
        return {
            'handle_id': self.handle_id,
            'name': self.name,
            'description': self.description,
            'rottnest_hash': self.rottnest_hash,
            'expands': expands
        }

    @classmethod
    def from_dict(cls, obj: dict):
        '''
            Reconstruction from dictionary
            Omits the parser
        '''
        return cls(**obj)
