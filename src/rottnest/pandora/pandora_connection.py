from pandora.pandora import Pandora, PandoraConfig

from rottnest.pandora.pandora_pg import pandora_pg_config_load, pandora_pg_default_path

# Internal singleton connection
# To ensure this is accessed in its latest state, must be accessed
# via `<module_name>.conn`
# (ie. importing the `conn` symbol gets a version corresponding to the
# AT-IMPORT value, which will most likely still be None)
# FUTURE: Wrap this so that it can be accessed w/out global and is mediated via a getter
conn = None

def load_pandora_connection(config_path=None):
    '''
        Loads the global singleton pandora connection
    '''
    global conn

    if conn is not None:
        # Already connected
        return True

    config_path = pandora_pg_default_path if config_path is None else config_path

    is_from_file, pgcfg = pandora_pg_config_load(config_path)
    config = PandoraConfig(**pgcfg)

    try:
        conn = Pandora(pandora_config=config, max_time=3600, decomposition_window_size=1000000)
    except:
        conn = None
        return False

    return True
