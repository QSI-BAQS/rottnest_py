import json
from functools import partial

class LuantiVisualiser: 
    '''
        LuantiVisualiser
        Visualiser object for Luanti from Rottnest 
        The visualiser json should be passed as an input  
        Layers may then be peeled using get_layer 
        The vtable object is constructed on first instantiation 
    '''

    _vtable = None
    ANCILLAE = 'Ancillae'
    DISTILL = 'DistllationQubit'
    REGISTER = 'Qubit'    

    DASHED = 'Dashed'
    SOLID = 'Solid'
    JOIN = 'AncillaeJoin'
    NONE = 'None'

    def __init__(self, vis_json):
        self.json_obj = vis_json
      
        # Binding at first instantiation of the class  
        # This avoids 
        if self._vtable is None: 
            # Inject the vtable
            LuantiVisualiser._vtable = { 
                'route': LuantiVisualiser.route,
                'reg': LuantiVisualiser.reg,
                'route_buffer': LuantiVisualiser.route_buffer,
                'cultivator': LuantiVisualiser.cultivator,
                'reserved': LuantiVisualiser.reserved,
                'bell': LuantiVisualiser.bell,
                'unused': LuantiVisualiser.unused,
                'factory_output': LuantiVisualiser.factory_output,
                'magic_state': LuantiVisualiser.magic_state,
            }

    def __len__(self):
        return len(self.json_obj['layers'])

    def get_layer(self, idx):
        '''
            Gets a layer for the visualiser
        '''
        layer = self.json_obj['layers'][idx]['board']
    
        # I will probably not apologise for the following code 
        mapped_layer = list(
            map(
                list, map(
                    partial(
                        map, self.obj_to_luanti
                    ),
                    layer
                )
            )
        )
        return mapped_layer

    def dump(self, fp): 
        '''
            TODO; Replace this with a generator
        '''
        layers = [self.get_layer(i) for i in range(len(self))]
        json.dump(layers, fp)

    @staticmethod 
    def obj_to_luanti(obj):
        '''
            Dispatch method to the class vtable
        ''' 
        return LuantiVisualiser._vtable[obj['type']](obj)
       
    @staticmethod
    def route(obj):
        if 'locked_by' in obj:
            return LuantiVisualiser.luanti_node(LuantiVisualiser.ANCILLAE, activity=None, text="", 
                top=LuantiVisualiser.JOIN, bottom=LuantiVisualiser.JOIN, left=LuantiVisualiser.JOIN, right=LuantiVisualiser.JOIN)
        else:
            return LuantiVisualiser.luanti_node(LuantiVisualiser.ANCILLAE, activity=None, text="")

    @staticmethod
    def reg(obj):
        return LuantiVisualiser.luanti_node(LuantiVisualiser.ANCILLAE, activity=None, text="", 
            top=LuantiVisualiser.SOLID, bottom=LuantiVisualiser.SOLID, left=LuantiVisualiser.DASHED, right=LuantiVisualiser.DASHED)

    @staticmethod
    def route_buffer(obj):
        return LuantiVisualiser.route(obj)

    @staticmethod
    def cultivator(obj):
        return LuantiVisualiser.factory_output(obj)

    @staticmethod
    def reserved(obj):
        return LuantiVisualiser.luanti_node(LuantiVisualiser.ANCILLAE)

    @staticmethod
    def bell(obj):
        return LuantiVisualiser.reg(obj)

    @staticmethod
    def unused(obj):
        return LuantiVisualiser.luanti_node(LuantiVisualiser.ANCILLAE)

    @staticmethod
    def factory_output(obj):
        return LuantiVisualiser.luanti_node(LuantiVisualiser.DISTILL, left=LuantiVisualiser.SOLID, top=LuantiVisualiser.SOLID)

    @staticmethod
    def magic_state(obj):
       return LuantiVisualiser.reg(obj) 

    @staticmethod
    def luanti_node(patch_type, activity=None, text="", left="None", right="None", bottom="None", top="None"):
     return {
        "activity": {
            "activity_type": activity  
        },
        "edges": {
            "Bottom": bottom,
            "Left": left,
            "Right": right,
            "Top": top 
         },
        "patch_type": patch_type, 
        "text": text
    }
