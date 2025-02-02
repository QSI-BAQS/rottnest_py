from itertools import cycle

from rottnest.input_parsers.qubit_label_tracker import QubitLabelTracker
from rottnest.input_parsers.rz_tag_tracker import RzTagTracker 
from rottnest.input_parsers.interrupt import INTERRUPT, NON_CACHING
from rottnest.compute_units.compute_unit import ComputeUnit
from rottnest.compute_units.architecture_proxy import ArchitectureProxy

from rottnest.pandora.pandora_translator import PandoraTranslator

from cabaliser.operation_sequence import OperationSequence

from pandora.pandora import Pandora, PandoraConfig



default = {
  "database":"postgres",
  "user":"alan",
  "host":"localhost",
  "port":"5555",
  "password":"1234"
}
# TODO make this nicer
config = PandoraConfig(**default)

pandora_connection = Pandora(pandora_config=config,
          max_time=3600,
          decomposition_window_size=1000000)

class PandoraSequencer():
    '''
        Pandora based widget sequencer
    '''

    def __init__(
            self,
            *architectures,
            sequence_length = 100,
            global_context = None,
            rz_tags = None,
            max_t = 10,
            max_d = 5,
            batch_size = 10
        ):

        self.pandora_connection = pandora_connection    

        self._architecture_proxies = list(map(ArchitectureProxy, architectures))
        self.sequence_length = sequence_length 
        if rz_tags is None:
            rz_tags = RzTagTracker() 
        self.rz_tags = rz_tags
    
        self.max_t = max_t
        self.max_d = max_d
        self.batch_size = batch_size

    def sequence_pandora(self):

        architectures = cycle(self._architecture_proxies)

        # Execution context
        architecture = next(architectures)
        compute_unit = ComputeUnit(architecture.to_json())       
        qubit_labels = QubitLabelTracker()
        rz_tags = self.rz_tags 
        operation_sequence = OperationSequence(5000)

        pandora_translator = PandoraTranslator()
 
        gate_count = 0

        widgets = self.pandora_connection.widgetize(
            max_t=self.max_t,
            max_d=self.max_d, 
            batch_size=self.batch_size, 
            add_gin_per_widget=True
        )

        for pandora_widget in widgets:
            print(pandora_widget)
            pandora_translator.translate_batch(
                pandora_widget,
                operation_sequence,
                qubit_labels,
                rz_tags
            )
            gate_count += len(operation_sequence)
          
            compute_unit.append(operation_sequence) 
            compute_unit.add_context(
                len(qubit_labels),
                rz_tags.n_rz_gates,
                len(qubit_labels),
            )

            yield compute_unit

            # Reset context
            compute_unit = ComputeUnit(
                next(architectures).to_json()
            ) 
            qubit_labels = QubitLabelTracker()
            rz_tags.reset()
            operation_sequence = OperationSequence(5000)

