from collections import Counter

from rottnest.architecture_interface import rottnest_composer

class RzCollectionResultsComposer(rottnest_composer.ResultsComposer):
    def __init__(self, result_dict=None, n_obj=1, comp_unit=None):
        super().__init__()

        if result_dict is None:
            result_dict = { "rz_counts" : Counter() }

        self._obj = result_dict

    def __add__(self, other):
        res = RzCollectionResultsComposer(
            result_dict = { "rz_counts": self._obj["rz_counts"] + other._obj["rz_counts"]},
            n_obj = self._n_obj + other._n_obj
        )

        res._unit_ids = self._unit_ids + other._unit_ids

        return res

    def __iadd__(self, other):
        self._unit_ids += other._unit_ids
        self._n_obj += other._n_obj
        self._obj["rz_counts"] += other._obj["rz_counts"]

        return self

    # TODO : Non-dummy value?
    def get_tocks(self):
        return 0

    def serialise(self):
        return f'{{"rz_counts": {dict(self._obj["rz_counts"])} }}'


class RzCollectionComposer(rottnest_composer.RottnestComposer):
    @staticmethod
    def results_composer_constructor():
        return RzCollectionResultsComposer
