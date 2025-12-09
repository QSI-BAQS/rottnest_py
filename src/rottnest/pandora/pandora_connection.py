from pandora.pandora import Pandora, PandoraConfig

from rottnest.pandora.pandora_pg import pandora_pg_config_load, pandora_pg_default_path

pandora_connection = None

def pandora_connect_glb(config_path=None):
    '''
        Somewhat bandaid-y fix to pandora connection being made at import time

        Loads the global singleton pandora connection

        Returns True on success, False on failure. Must not be re-called if successful
    '''
    global pandora_connection

    config_path = pandora_pg_default_path if config_path is None else config_path

    is_from_file, pgcfg = pandora_pg_config_load(config_path)
    config = PandoraConfig(**pgcfg)

    if pandora_connection is not None:
        raise Exception("Pandora connection already exists. pandora_connect_glb() must be called successfully at most once")

    try:
        pandora_connection = Pandora(pandora_config=config, max_time=3600, decomposition_window_size=1000000)
    except:
        pandora_connection = None
        return False

    return True


