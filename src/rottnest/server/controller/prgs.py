import json
from rottnest.server.responder import responder

@responder.register('process_list')
def process_load_list(app, message, **kwargs):
    '''
       Retrieves a list of processes (program instances)
       that are being managed

       No data is required to be sent
    '''
    #exemap = app.get_extensions().get_exe_map()
    #prgslist = exemap.get_circuits()
    
    return {
        'err': 'currently not implemented'
    }

@responder.register('program_get_config')
def program_get_config(app, message, **kwargs):
    '''
       Constructs the configuration file
       that the executable_map has formed
    '''
    prgmap = app.get_extensions().get_exe_map()
    config = prgmap.to_config()
    return { 'config' : config }
    
@responder.register('program_set_config')
def program_set_config(app, message, **kwargs):
    '''
        Constructs and updates the current executable map
        from a configuration object
    '''
    cfg = json.loads(message['payload']['config'])
    print(str(cfg))
    prgmap = app.get_extensions().get_exe_map()
    res = prgmap.from_dict_interior_update(cfg)
    return { 'success' : res }

    
@responder.register('program_list')
def program_load_list(app, message, **kwargs):
    '''
       Retrieves the list of programs that have been registered
       with the application

       No data is required to be sent
    '''
    prgmap = app.get_extensions().get_exe_map()
    prglist = prgmap.get_circuit_dtos()
    return {
        "prg_list": prglist
    }



@responder.register('program_get_current')
def program_get_current(app, message, **kwargs):
    '''
       Gets the currently selected program

       Does not require any data to be sent 
    '''
    exestate = app.get_extensions().get_exe_state()
    prg = exestate.get_program()

    return {
        "prg": prg
    }

@responder.register('program_get')
def program_get(app, message, **kwargs):
    '''
       Gets a program from the exe_map

        {
            prg_name : <string> 
        }
       
    '''
    prg_name = message['payload']['prg_name']
    prgmap = app.get_extensions().get_exe_map()
    prg = prgmap.get_circuit_desc(prg_name)

    # TODO: Error if the program can't be accessed

    return {
        "prg_desc": prg
    }

@responder.register('program_set_current')
def program_set(app, message, **kwargs):
    '''
        Set the program name to be used
        Will return a confirmed object back to the frontend
        to outline if it was successful or not
        {
             prg_name: <string>,
             prg_args: [<number>,...]
        }
        
    '''
    
    prg_name = message['payload']['prg_name']
    prg_args = message['payload']['prg_args']
    
    prgmap = app.get_extensions().get_exe_map()

    prg = prgmap.get_circuit(prg_name)
    
    ret_obj = {
        'success': False,
        'message': 'Unable to set Program, it does not exist'
    }
    if prg is not None:
        prgstate = app.get_extensions().get_exe_state()
        prgstate.set_program(prg, prg_args)
        ret_obj = {
            'success': True,
            'message': "Program has been set"
        }
        
    else:
        print("Unable to set Program, it does not exist")

    return ret_obj
