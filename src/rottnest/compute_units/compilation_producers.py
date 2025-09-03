'''
    Production functions for compilation units 
'''

from types import GeneratorType

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.compute_units.sequencer import Sequencer
from rottnest.compute_units.compute_unit import ComputeUnit 

def generate_compute_units(
        layout_ids: list[int],
        architecture: 'RottnestArchitecture',
        executable: 'RottnestExecutable'
    ) -> GeneratorType:
    '''
        Generates compute units for distribution 
        This forms a producer / consumer pattern 
    '''
    # Drops cache if the architecture changes
    PyliqtrParser.set_cache_tag(layout_ids)

    parser = PyliqtrParser(executable())
    parser.parse()
    
    seq = Sequencer(*layout_ids)
    it = seq.sequence_pyliqtr(parser)

    return it


def generate_graph_states(
        layout_ids: list[int],
        architecture: 'RottnestArchitecture',
        executable: 'RottnestExecutable'
    ) -> GeneratorType:
        '''
            Generates graph states for distribution
        '''
        ...

