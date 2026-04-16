from rottnest.plugins import architectures
from rottnest.compute_units.layout_proxy import LayoutProxy

class Visualiser:
    '''
        More singleton
    '''
    current_worker = None
    current_compute_unit = None

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
        it = seq.sequence_pylitqr(parser)
        return it

    @classmethod
    def setup_worker(cls):
        '''
            Worker setup function
            Called to flush the worker when appropriate
        '''
        arch = architectures.get_current_architecture()
        worker = arch.worker(LayoutProxy.get_layouts())

    @classmethod
    def run_visualiser(cls, compute_unit):
        '''
            Runs the visualiser
        '''

        # Worker with no queues attached
        current_compute_unit() 

    def next():
        '''
        '''
