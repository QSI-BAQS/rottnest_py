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
    #prgmap = app.get_extensions().get_exe_map()
    #config = prgmap.to_config()
    #return { 'config' : config }
    return {
        'err': 'currently not implemented'
    }
    
@responder.register('program_set_config')
def program_set_config(app, message, **kwargs):
    '''
        Constructs and updates the current executable map
        from a configuration object
    '''
    #cfg = json.loads(message['payload']['config'])
    #print(str(cfg))
    #prgmap = app.get_extensions().get_exe_map()
    #res = prgmap.from_dict_interior_update(cfg)
    #return { 'success' : res }
    return {
        'err': 'currently not implemented'
    }

    
@responder.register('program_list')
def program_load_list(app, message, **kwargs):
    '''
       Retrieves the list of programs that have been registered
       with the application, this also includes parameters
    '''
    prgmap = app.get_extensions().get_exe_map()
    prglist = []
    for k, e in prgmap.get_executables().items():

        newparams = list(map(lambda f: (f[0], str(f[1][0].__name__), f[1][1]), e.get_parameters().items()))
        print(newparams)
        obj = {
            'prgname': k,
            'prgparams': newparams
        }
        prglist.append(obj)
    
    return {
        "prglist": prglist
    }



@responder.register('program_get_current')
def program_get_current(app, message, **kwargs):
    '''
       Gets the currently selected program

       Does not require any data to be sent 
    '''
    exestate = app.get_extensions().get_exe_state()
    prgname = exestate.get_current_executable().get_name()
    params = exestate.get_executable_params()
    
    return {
        "prgname": prgname,
        "prgparams": params
    }


@responder.register('program_set_current')
def program_set(app, message, **kwargs):
    '''
        Set the program name to be used
        Will return a confirmed object back to the frontend
        to outline if it was successful or not
        {
             prgname: <string>,
             prgargs: <dict> - Key is param, value is arg
        }
        
    '''
    
    prg_name = message['payload']['prgname']
    prg_args = message['payload']['prgargs']
    
    prgmap = app.get_extensions().get_exe_map()

    print(prg_name)
    print(prg_args)
    prgmap.set_current_executable(prg_name)

    nprg_args = {}
    for a in prg_args:
        param_key = a[0]
        arg = a[2]
        nprg_args[param_key] = arg

    nprg_args
    
    prgmap.set_current_executable_args(nprg_args)
        
    prgname = prgmap.get_current_executable().get_name()
    params = prgmap.get_executable_params()
    

    ret_obj = {
        'prgname': prgname,
        'prgparams': params
    }
        
    return ret_obj
