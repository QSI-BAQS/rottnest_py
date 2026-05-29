from rottnest.plugins import architectures
from rottnest.compute_units.layout_proxy import LayoutProxy
from rottnest.input_parsers.interrupt import INTERRUPT
from rottnest.compute_units.sequencer import Sequencer


class Visualiser:
    '''
        More singleton
    '''
    ENDCOMP = object()
    current_worker = None
    current_sequence = None

    @classmethod
    def build_compute_units(
            cls,
            parser, 
            layout_ids=None
        ) -> "iter<ComputeUnit>":
        '''
        '''
        if layout_ids is None:
            layout_ids = [0]

        seq = Sequencer(*layout_ids)
        it = seq.sequence_pyliqtr(parser)
        cls.current_sequence = it
        return it

    @classmethod
    def setup_worker(cls):
        '''
            Worker setup function
            Called to flush the worker when appropriate
        '''
        arch = architectures.get_current_architecture()
        cls.current_worker = arch.worker(
            LayoutProxy.get_layouts()
        )

    @classmethod
    def run_visualiser(
            cls, 
            compute_unit: "ComputeUnit"
            ):
        '''
            Runs the visualiser
        '''
        
        # Worker with no queues attached
        result = cls.current_worker.execute_compute_unit_visualiser(
            compute_unit
        )
        return result

    @classmethod
    def next(cls):
        '''
            Compiles and runs the next visualisation
            in the sequence
        '''
        
        state = True 
        while cls.ENDCOMP is not(
                compute_unit := next(
                    cls.current_sequence,
                    cls.ENDCOMP
                )
            ):
            if compute_unit != INTERRUPT:
                return cls.run_visualiser(compute_unit)

        return None
