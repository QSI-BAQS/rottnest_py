from itertools import cycle

from cabaliser.operation_sequence import OperationSequence
from pandora.pandora import Pandora, PandoraConfig

from rottnest.input_parsers.qubit_label_tracker import QubitLabelTracker
from rottnest.input_parsers.rz_tag_tracker import RzTagTracker 
from rottnest.input_parsers.interrupt import INTERRUPT, NON_CACHING
from rottnest.compute_units.compute_unit import ComputeUnit
from rottnest.compute_units.architecture_proxy import ArchitectureProxy

from rottnest.pandora.pandora_translator import PandoraTranslator
from rottnest.pandora.pandora_qubit_label_tracker import PandoraQubitLabelTracker

from rottnest.pandora.proxy_cirq_parser import ProxyCirqParser

from rottnest.pandora.pandora_pg import pandora_pg_config_load, pandora_pg_default_path

is_from_file, pgcfg = pandora_pg_config_load(pandora_pg_default_path)
config = PandoraConfig(**pgcfg)

#try:
pandora_connection = Pandora(pandora_config=config,
          max_time=3600,
          decomposition_window_size=1000000)
#except:
#    pandora_connection = None
#print("Connection to Pandora failed")


class PandoraGate:
    def __init__(self, name):
        self.gate = name

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
            max_t = 100,
            max_d = 100,
            batch_size = 100,
            conn = None,
            name = None
        ):
        self.fully_decomposed = True

        self.op = PandoraGate(name)

        if conn is None:
            conn = pandora_connection    
        self.pandora_connection = conn 

        if len(architectures) == 0:
            self._architecture_proxies = [None]
        else:
            self._architecture_proxies = list(map(ArchitectureProxy, architectures))
        self.sequence_length = sequence_length 
        if rz_tags is None:
            rz_tags = RzTagTracker() 
        self.rz_tags = rz_tags
    
        self.max_t = max_t
        self.max_d = max_d
        self.batch_size = batch_size

    def set_sequence_length(self, sequence_length: int):
        '''
            Setter for sequence length
        '''
        self.sequence_length = sequence_length

    def set_max_t(self, max_t: int):
        '''
            Setter for max_t 
        '''
        self.max_t = max_t
       
    def set_max_t(self, max_t: int):
        '''
            Setter for max_t 
        '''
        self.max_t = max_t

    def set_max_d(self, max_d: int):
        '''
            Setter for max_d 
        '''
        self.max_d = max_d

    def set_batch_size(self, batch_size: int):
        '''
            Setter for batch_size 
        '''
        self.batch_size = batch_size

    def set_params(
        self,
        *,  # Kwargs only
        sequence_length: int | None = None,
        max_t: int | None = None,
        max_d: int | None = None,
        batch_size: int | None = None):
        '''
            Multi-parameter setter
        '''

        if sequence_length is not None: 
            self.sequence_length = sequence_length

        if max_t is not None: 
            self.max_t = max_t

        if max_d is not None: 
            self.max_d = max_d

        if batch_size is not None: 
            self.batch_size = batch_size

    def traverse(self):
        '''
            Returns proxied cirq parser objects
        '''
        for compute_unit in self.sequence_pandora():
            yield ProxyCirqParser(compute_unit.op_seq, len(compute_unit))
          
    def parse(self):
        '''
            No further parsing needed
        '''
        pass

    def to_operation_sequence(self):
        return self.sequence_pandora()

    def decompose(self):
        print("Decomposing")
        for i in self.sequence_pandora():
            print(i)
            yield i
        return

    def sequence_pandora(self):
        architectures = cycle(self._architecture_proxies)

        # Execution context
        architecture = next(architectures)
        if architecture is not None:
            compute_unit = ComputeUnit(architecture.to_json())       
        else:
            compute_unit = ComputeUnit(None)       
        qubit_labels = PandoraQubitLabelTracker()
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

            if compute_unit.n_gates == 0:
                continue

            print(f"Unit: {len(compute_unit.sequences[0])}")
            yield compute_unit

            # Reset context
            compute_unit = ComputeUnit(
                next(architectures).to_json()
            ) 
            qubit_labels = PandoraQubitLabelTracker()
            rz_tags.reset()
            operation_sequence = OperationSequence(5000) 
