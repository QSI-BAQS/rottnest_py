from functools import lru_cache

# Ill advised, but forces the generation and capture of the region types
from t_scheduler.widget import * 
from t_scheduler.widget.region_types import region_types 

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
