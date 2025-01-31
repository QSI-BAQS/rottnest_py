import json
from functools import partial

class LuatiVisualiser: 
    '''
        LuatiVisualiser
        Visualiser object for Luati from Rottnest 
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
            LuatiVisualiser._vtable = { 
                'route': LuatiVisualiser.route,
                'reg': LuatiVisualiser.reg,
                'route_buffer': LuatiVisualiser.route_buffer,
                'cultivator': LuatiVisualiser.cultivator,
                'reserved': LuatiVisualiser.reserved,
                'bell': LuatiVisualiser.bell,
                'unused': LuatiVisualiser.unused,
                'factory_output': LuatiVisualiser.factory_output,
                'magic_state': LuatiVisualiser.magic_state,
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
                        map, self.obj_to_luati
                    ),
                    layer
                )
            )
        )
        return mapped_layer

    @staticmethod 
    def obj_to_luati(obj):
        '''
            Dispatch method to the class vtable
        ''' 
        return LuatiVisualiser._vtable[obj['type']](obj)
       
    @staticmethod
    def route(obj):
        if 'locked_by' in obj:
            return LuatiVisualiser.luati_node(LuatiVisualiser.ANCILLAE, activity=None, text="", 
                top=LuatiVisualiser.JOIN, bottom=LuatiVisualiser.JOIN, left=LuatiVisualiser.JOIN, right=LuatiVisualiser.JOIN)
        else:
            return LuatiVisualiser.luati_node(LuatiVisualiser.ANCILLAE, activity=None, text="")

    @staticmethod
    def reg(obj):
        return LuatiVisualiser.luati_node(LuatiVisualiser.ANCILLAE, activity=None, text="", 
            top=LuatiVisualiser.SOLID, bottom=LuatiVisualiser.SOLID, left=LuatiVisualiser.DASHED, right=LuatiVisualiser.DASHED)

    @staticmethod
    def route_buffer(obj):
        return LuatiVisualiser.route(obj)

    @staticmethod
    def cultivator(obj):
        return LuatiVisualiser.factory_output(obj)

    @staticmethod
    def reserved(obj):
        return LuatiVisualiser.luati_node(LuatiVisualiser.ANCILLAE)

    @staticmethod
    def bell(obj):
        return LuatiVisualiser.reg(obj)

    @staticmethod
    def unused(obj):
        return LuatiVisualiser.luati_node(LuatiVisualiser.ANCILLAE)

    @staticmethod
    def factory_output(obj):
        return LuatiVisualiser.luati_node(LuatiVisualiser.DISTILL, left=LuatiVisualiser.SOLID, top=LuatiVisualiser.SOLID)

    @staticmethod
    def magic_state(obj):
       return LuatiVisualiser.reg(obj) 

    @staticmethod
    def luati_node(patch_type, activity=None, text="", left="None", right="None", bottom="None", top="None"):
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
