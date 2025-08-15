# TODO Replace this with the programme switcher
from t_scheduler.rottnest_interface import architectures as t_architectures

# Module static variable
architectures = {}

for architecture in rottnest_interface.architectures.architectures: 
    architectures[architecture.get_name()] = architecture 

current_architecture = next(iter(architectures.values()))


def set_architecture(self, key):
    '''
        Setter for the architecture
    '''
    current_architecture = architectures.get(key, None)
    if current_architecture is None:
        raise Exception(f"Unknown architecture {key}")

