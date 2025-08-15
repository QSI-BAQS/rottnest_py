


def run_widget(archobj, widget_package):
    """
       run_widget: Will run the widget based on a generic
       package 
    """
    archobj.arch_make_graph_state(widget_package)
    archobj.arch_make_pseudo_gates(widget_package)
    archobj.arch_make_layout(widget_package)
    archobj.arch_make_actual_gates(widget_package)
    archobj.arch_make_mapper(widget_package)
    
    # Will need to outline what is required here
    # Returned object for it to be managed by the python
    # backend is likely needed
    archobj.arch_construct_widget(widget_package)
    orc = archobj.arch_construct_orchestrator(widget_package)

    return orc
    


