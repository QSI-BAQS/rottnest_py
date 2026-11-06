'''
    Constants for process pool messaging
'''
from rottnest import plugins

PING = 'ping'
POLL = 'poll'
PING_MANAGER = 'ping_mgr'

START_WORKERS = 'start_workers'
STOP_WORKERS = 'stop_workers'

TERMINATE = 'terminate'
RUN_SEQUENCE = 'run_sequence'

SET_OPTION = 'set_option'
SET_OPTIONS = 'set_options'
GET_OPTIONS = 'get_options'

SET_RZ_PRECISION = 'set_rz_precision'

RESET_EXECUTION_CONTEXT = 'reset_execution_context'

# Synchronise executable and architecture modules
# With the manager
SYNCHRONISE_MODULES = 'synchronise_modules'

# Synchronises layouts with the manager process
SYNCHRONISE_LAYOUTS = 'synchronise_layouts'

# Debug command for getting status of elements
SYNCHRONISATION_STATUS = 'synchronisation_status'

# Sends current results to the manager 
# Priority task
GET_CURRENT_RESULTS = 'get_current_results'
GET_RESULTS_STREAM = 'get_results_stream'
GET_POSTPROCESSING_DATA = 'get_postprocessing_data'

# Postprocessing
# This will probably eventually just fall under the
# plugin system
SET_POSTPROCESSOR_PARAMETERS = 'set_postprocessor'
GET_POSTPROCESSOR_PARAMETERS =  'get_postprocessor'
RUN_POSTPROCESSOR =  'run_postprocessor'



