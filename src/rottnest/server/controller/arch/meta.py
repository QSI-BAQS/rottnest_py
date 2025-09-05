import json
from rottnest.server.responder import responder

    
@responder.register('arch_list')
def arch_load_list(app, message, **kwargs):
    '''
       Retrieves the list of archs that have been registered
       with the application

       No data is required to be sent
    '''
    archmap = app.get_extensions().get_arch_map()
    
    #archlist = archmap.get_arch_dtos()
    archlist = []
    archs = archmap.get_architectures()
    
    for k, a in archs.items():
        archlist.append([k, a.designer().get_designer_metadata()])
    
    return {
        "arch_list": archlist
    }


@responder.register('arch_set')
def arch_set(app, message, **kwargs):
    key = message['payload']['arch_name']
    amap = app.get_extensions().get_arch_map()
    amap.set_current_architecture(key)

    return {
        'arch': key
    }

@responder.register('arch_get_config')
def arch_get_config(app, message, **kwargs):
    '''
       Gets the current configuration that was successfully loaded 
    '''
    archmap = app.get_extensions().get_arch_map()
    cfg = archmap.to_config()

    return { 'config' : cfg }

@responder.register('arch_set_config')
def arch_set_config(app, message, **kwargs):
    '''
        Takes the current architecture config from
        the frontend and attempts to update the configuratio
    '''
    cfg = json.loads(message['payload']['config'])
    archmap = app.get_extensions().get_arch_map()
    res = archmap.from_dict_interior_update(cfg)
    
    return {
        "success": res
    }


@responder.register('arch_get')
def program_get(app, message, **kwargs):
    '''
        Gets an architecture details
        {
            arch_name : <string> 
        }

        The architecture details will include a schema for
        its api mapping

        This is used by the front-end to know what
        endpoints to hit
       
    '''
    arch_name = message['payload']['arch_name']
    archmap = app.get_extensions().get_arch_map()
    arch = archmap.get_arch_desc(arch_name)

    return {
        "arch": arch
    }

