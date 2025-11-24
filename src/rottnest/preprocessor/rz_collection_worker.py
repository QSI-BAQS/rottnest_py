from collections import Counter

from rottnest.architecture_interface.rottnest_worker import RottnestWorker

class RzCollectionWorker(RottnestWorker):

    COUNTER = 'rz_counts'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_stats(
            self,
            compiled_widget,
            compute_unit,
            non_participatory_qubits
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
            rz_tag_tracker_dict: dict
        ):
        # TODO : Is it possible to map widget (JSON) back to gates?
        raise NotImplementedError

    def execute_compute_unit(
            self,
            compute_unit: "ComputeUnit"
        ):
        '''
            For an rz collector, execution is just counting rz by tag
        '''
        rz_counter = Counter()
        rz_tracker = compute_unit.extract_rz_tracker()
        for seq in compute_unit.sequences:
            for op in seq:
                if op.is_rz():
                    # Map tag back to actual angle
                    rz_counter[rz_tracker[op.rz.tag]] += 1

        return { self.COUNTER: rz_counter }
    
    def set_precision(self, precision):
        '''
            No need to set precision
        '''
        pass
