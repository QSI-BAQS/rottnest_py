from functools import lru_cache
import random

# Ill advised, but forces the generation and capture of the region types
from t_scheduler.widget import * 
from t_scheduler.widget.region_types import region_types, region_args

from t_scheduler.router import *
from t_scheduler.router import region_router_exports

from rottnest.widget_compilers.main import run as run_widget

saved_architectures = {}

@lru_cache
def get_region_subtypes() -> str: 
    '''
        Extracts the region subtypes from the t_scheduler
        Exposes the names of the regions as a json object
    '''
    # Import architecture, get subtype names
    return {i: list(region_types[i].keys()) for i in region_types}
   
def get_factory_types() -> str: 
    return ''

def run_widget_scheduler(arch_id):
    result = run_widget(region_obj=saved_architectures[arch_id])
    return result.json

def get_router_mapping():
    return region_router_exports

def save_arch(arch_obj):
    arch_id = random.randint(1000000, 9999999)
    while arch_id in saved_architectures: arch_id = random.randint(1000000, 9999999)

    saved_architectures[arch_id] = arch_obj
    return arch_id

def get_region_arguments():
    return region_args
