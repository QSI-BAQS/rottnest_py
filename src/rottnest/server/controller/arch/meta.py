
from rottnest.server.responder import responder

    
@responder.register('arch_list')
def arch_load_list(app, message, **kwargs):
    '''
       Retrieves the list of archs that have been registered
       with the application

       No data is required to be sent
    '''
    archmap = app.get_extensions().get_arch_map()
    archlist = archmap.get_arch_dtos()
    return {
        "arch_list": archlist
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

    # TODO: Error if the program can't be accessed

    return {
        "arch": arch
    }

