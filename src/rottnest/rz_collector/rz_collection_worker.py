from collections import Counter

from rottnest.architecture_interface.rottnest_worker import RottnestWorker

class RzCollectionWorker(RottnestWorker):

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

    def execute_compute_unit(
            self,
            compute_unit: "ComputeUnit"
        ):
        '''
            For an rz collector, execution is just counting rz by tag
        '''
        rz_counter = Counter()
        for seq in compute_unit.sequences:
            for op in seq:
                if op.is_rz():
                    rz_counter[op.rz.tag] += 1

        return { "rz_counts": rz_counter }
