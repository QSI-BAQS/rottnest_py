
import json
from rottnest.executables.circuit import CircuitDescription
from rottnest.executables.fermi_hubbard import make_fh_circuit

class ExecutableMap:
    '''
       Executable map that will hold onto references
       to circuits that it can construct 
    '''

    def __init__(self):
        '''
           Constructor, creates an empty
           map along with generating an
           instance that can be invoked
            
        '''
        self.circuit_map = {}
        self.circuit_instances = []


    @staticmethod
    def from_config_or_default(path):
        '''
           Constructs a map from json file
           If the path does not exist or
           the data cannot be parsed,
           a new map will be created but a
           warning will show 
        '''
        exe_map = ExecutableMap()
        try:
            with open(path, 'r') as f:
                data = f.read()
                cfg = json.loads(data)
                for entry in cfg:

                    circ_res = CircuitDescription.create_circuit_from(entry)
                    if circ_res is not None:
                        exe_map.insert_circuit_desc(circ_res)
        except Exception:
        
            print("Unable to open file, likely missing, using defaults")
            
            # TODO: Hold this in a list in another module
            circ_dict = {
                'name': "fermi_hubbard",
                'invoke_fn': make_fh_circuit,
                'args' : [2, 1.0, 0.95],
                'params': ['N', 'times', 'p_algo']
                
            }
            circ_res = CircuitDescription.create_circuit_from_dict(circ_dict)
            exe_map.insert_circuit_desc(circ_res)
            
        return exe_map
    
    
    def insert_circuit_desc(self, circ_desc):
        '''
           Inserts a description to the map
           This acts as a factory mechanism 
        '''
        if isinstance(circ_desc, CircuitDescription): 
            self.circuit_map[circ_desc] = circ_desc
        else:
            print("Unable insert description")

    def get_circuits(self):
        '''
           Gets a list of circuits 
        '''
        return self.circuit_map.values()

    def get_circuit_dtos(self):
        '''
           Gets a list of circuits in DTO form
        '''
        prg_descs = []
        for k, p in self.circuit_map:
            prg_descs.append(p.to_dto())

        return prg_descs

    def get_circuit_desc(self, name):
        '''
           Retrieves a description, not typically that
           this is useful by itself 
        '''
        return self.circuit_map[name]

    def make_instance_from(self, name, args=None):
        '''
           Creates an instance of registered circuit 
        '''
        return self.get_circuit_desc(name).create_instance()
        
    def make_instance_from_and_ref(self, name, args=None):
        '''
           Similar to make_instance_from
           but will also hold a reference 
        '''
        obj = self.make_instance_from(name, args)
        self.circuit_instances.append(obj)
        return obj
