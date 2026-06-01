from rottnest.compute_units.layout_proxy import LayoutProxy

t_error_string = "Id {} is not of type int"

def setup_layout(*p_args, **p_kwargs):
    '''
        Decorator setup for reseting layout proxy context between tests
        :: p_args : <Layout> :: Ordered list of layouts
        :: p_kwargs : {id: <Layout>} :: Id Map of layouts 
        The ID mapped layouts may override ordered layouts
    '''
    def _proxies(fn):
        # Clear layouts
        LayoutProxy.flush() 
       
        # Ordered args 
        for layout in p_args:
            LayoutProxy.add_layout(layout)

        # Kwargs
        for layout_id, layout in p_kwargs.items():
            # Check that the layout is mapped to an integer
            if not isinstance(layout_id, int):
                raise TypeError(t_error_string.format(layout_id))

            # Add the layout
            LayoutProxy.add_layout_with_id(layout_id, layout)

        # Invoke the decorated function
        def _wrap(*args, **kwargs):
            return fn(*args, **kwargs)
        return _wrap
    
    return _proxies
