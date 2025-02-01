from itertools import cycle

from rottnest.input_parsers.qubit_label_tracker import QubitLabelTracker
from rottnest.input_parsers.interrupt import INTERRUPT, NON_CACHING
from rottnest.compute_units.compute_unit import ComputeUnit
from rottnest.compute_units.architecture_proxy import ArchitectureProxy

from rottnest.pandora.pandora_translator import PandoraTranslator

from cabaliser.operation_sequence import OperationSequence

class PandoraSequencer():
    '''
        Pandora based widget sequencer
    '''

    def __init__(
            self,
            pandora_connection,
            *architectures,
            sequence_length = 100,
            global_context = None,
            rz_tags = None
        ):

        self.pandora_connection = pandora_connection    
        self._architecture_proxies = list(map(ArchitectureProxy, architextures))
        self.sequence_length = sequence_length 
        if rz_tags is None:
            rz_tags = RzTagTracker() 
        self.rz_tags = rz_tags


    def sequence_pandora(self, pandora_parser):

        architectures = cycle(self._architecture_proxies)

        # Execution context
        architecture = next(architectures)
        compute_unit = ComputeUnit(architecture.to_json())       
        qubit_labels = QubitLabelTracker()
        rz_tags = self.rz_tags 

        pandora_translator = PandoraTranslator()
 
        gate_count = 0
        for pandora_widget in pandora_generator:
            pandora_translator.translate_batch(
                pandora_widget,
                operation_sequence,
                qubit_labels,
                rz_tags
            )
            gate_count += len(operation_sequence)
           
            compute_unit.add_context(
                qubit_labels
            )

            yield compute_unit

            # Reset context
            compute_unit = Compute_unit(
                next(architectures).to_json()
            ) 
            qubit_labels = QubitLabelTracker()
            rz_tags.reset()
