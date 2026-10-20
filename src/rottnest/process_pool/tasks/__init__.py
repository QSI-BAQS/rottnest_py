'''
    Force import all for collector patterns
'''
from .pool_task import PoolTask, get_pool_manager_tasks 
from . import ping
from . import set_option
from . import synchronise_modules 
from . import synchronise_layouts
from . import set_rz_precision
from . import terminate

# Bind collected objects to namespace
for task in get_pool_manager_tasks().values():
    locals()[task.__class__.__name__] = task
