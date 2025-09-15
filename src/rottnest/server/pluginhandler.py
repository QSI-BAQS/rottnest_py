from bottle import static_file


PLUGIN_ROUTE = '/plugin/<archname:string>/schema/<filename:path>'


def register_routes(app, path):
    '''
        Registers the routes for the plugin schema loader
        TODO: Args not passed 
    '''
    arch_des_route = plugin_schema_file_fn_generator()
    app.route(PLUGIN_ROUTE, callback=arch_des_route)


def plugin_schema_file_fn_generator(filename, rootpath):
    '''
        Designer file would likely be loaded via this pathway
    '''
    def plugin_viz_get_file(archname, filename):
        return static_file(f"{archname}/schema/{filename}", root=rootpath)

    return plugin_viz_get_file

