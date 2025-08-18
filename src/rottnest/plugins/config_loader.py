'''
    Loads configuration files
'''

import os

import typing

from .. import config

def default_loader(
        config_file_name: str,
        constructor: typing.Type['PluginManager'],
        ) -> 'PluginManager':
    '''
        default_loader

        Generic loader for configuration files to
        the plugin manager.
        Checks each location specified in the
        configuration file, attempts to load using
        the provided constructor and returns the
        created plugin manager
    '''

    for loc in config.configuration_locations:
        # TODO: Consider composing multiple configs
        # rather than just using the first
        config_path = f'{loc}/{config_file_name}'

        # Check if file exists
        # File error handling is managed in the
        # constructor
        if os.path.isfile(config_path):
            return constructor(
                config_path=config_path
            )

    print("No configuration files found")
    # No configuration files found
    return constructor()
