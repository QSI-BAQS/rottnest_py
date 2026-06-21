'''
    Rz Collector worker object
'''
from rottnest.architecture_interface.rottnest_worker import RottnestWorker

from .rz_collection_composer import RzCollectionResultsComposer


class RzCollectionWorker(RottnestWorker):
    '''
        Worker for Rz collection
    '''

    def __init__(self, *args, **kwargs):
        '''
            Constructor
        '''
        super().__init__(*args, **kwargs)

    def get_stats(
            self,
            compiled_widget,
            compute_unit,
            _non_participatory_qubits
            ) -> dict:
        '''
            Extract stats (in this case, just the rz totals)
        '''
        return self.execute_compute_unit(compute_unit)

    def execute_graph_state(
                self,
                unit_id: int,
                layout_id: int,
                widget_json: dict,
                rz_tag_tracker: dict
            ):
        '''
            The collector only works on compute units
        '''
        raise NotImplementedError

    def execute_compute_unit(
                self,
                compute_unit: "ComputeUnit"
            ):
        '''
            For an rz collector, execution is just counting rz by tag
        '''
        rz_counter = RzCollectionResultsComposer(
            unit_id=compute_unit.unit_id
        )
        rz_tracker = compute_unit.extract_rz_tracker()
        for seq in compute_unit.sequences:
            for op in seq:
                if op.is_rz():
                    # Map tag back to actual angle
                    rz_counter.tally(
                        rz_tracker[op.rz.tag]
                    )
        return compute_unit.unit_id, rz_counter

    def set_precision(self, precision) -> None:
        '''
            No need to set precision
        '''
