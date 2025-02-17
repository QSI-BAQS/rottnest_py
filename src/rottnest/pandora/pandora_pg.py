import os
import json

pandora_pg_default_path = 'pandora_pg.json'
default_cfg = {
  "database":"postgres",
  "user":"postgres",
  "host":"localhost",
  "port":"5555",
  "password":"1234"
}


class PandoraPGValidationError(Exception):
    '''
    Exception to be raised if a type is missing or incorrect
    could be its own validator
    '''
    pass

class PandoraPGKeyMissingError(Exception):
    '''
    Exception raised if a key required is missing from the config
    May be removed because the db config is too strict to be reasonable
    '''
    pass

def pandora_pg_config_load(path):
    '''
    Loads postgres config file of a specified path
    to use pandora database
    
    If the file cannot be loaded or key validation fails
    or type validation fails, it will load the default setup

    Returns a tuple with:
        (success_state, obj)
    '''
    cfgkey_types = [('database', str), ('user', str), ('host', str), 
               ('port', str), ('password', str)]
    
    cfgpath = ''.join([os.getcwd(),'/',path]) 
    print(cfgpath) 
    try: 
        cfgfile = open(cfgpath, 'r')
        cfglines = ''.join(cfgfile.readlines())
        try:
            pgdata = json.loads(cfglines)
            # TODO: Validate the config file 
            for kt in cfgkey_types:
                cfgk, cfgt = kt
                if cfgk not in pgdata:
                    raise PandoraPGKeyMissingError
                if type(pgdata[cfgk]) is not cfgt:
                    raise PandoraPGValidationError

            return (True, pgdata)
        except PandoraPGKeyMissingError as pgerr:
            print('Key missing in pandora-postgres configuration')
        except PandoraPGValidationError as pgerr:
            print('Validation on pandora-postgres configuration failed')
        except Exception as err:
            print(err)
            print('Unable to parse pandora-postgres config')
    except:
        print('Unable to open file, using default')

    return (False, default)
