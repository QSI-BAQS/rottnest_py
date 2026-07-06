'''
    Results composer implementing Rz counting
    This is useful for preprocessing and determining Rz precisions
    and T factory fidelties
'''

from rottnest.architecture_interface import rottnest_composer

RZ_COUNTS = 'rz_counts'


class RzCollectionResultsComposer(rottnest_composer.ResultsComposer):
    '''
        Composer for Rz tags
    '''
    def __init__(self, result_obj=None, n_obj=1, unit_id=None, CACHED=False):
        '''
            Constructor
        '''
        if result_obj is None:
            result_obj = {}

        super().__init__(
            result_obj=result_obj,
            n_obj=n_obj,
            unit_id=unit_id,
            CACHED=CACHED # NOTE: Mixup on constructor usage
        )

    def __add__(self, other):
        '''
            Overloaded add operator
            Performs linear composition of Results
        '''
        base_obj = dict(self._obj)

        for key, value in other._obj.items():
            base_obj[key] = base_obj.get(key, 0) + value

        res = RzCollectionResultsComposer(
            result_obj=base_obj,
            n_obj=self._n_obj + other._n_obj
        )

        res._unit_ids = self._unit_ids + other._unit_ids

        return res

    def __iadd__(self, other):
        '''
            Iadd using add
        '''
        self._unit_ids += other._unit_ids
        self._n_obj += other._n_obj

        for key, value in other._obj.items():
            self._obj[key] = self._obj.get(key, 0) + value
        return self

    def tally(self, tag, num=1) -> None:
        '''
            Tracks an rz
        '''
        if tag in self._obj:
            self._obj[tag] += num
        else:
            self._obj[tag] = num

    def get_tagged_rz_counts(self) -> dict:
        '''
            Gets tagged rz counts
        '''
        return self._obj

    def get_n_rz(self):
        '''
            Gets the total number of rz_gates
        '''
        return sum(self.get_tagged_rz_counts().values())

    def get_tocks(self):
        '''
            Dummy value
        '''
        return 0

    def get_sequential_tocks(self):
        return 0

    def to_args(self):
        '''
            Serialisation
        '''
        return self._obj

    @classmethod
    def from_args(cls, results_dict, unit_id=None):
        return cls(results_dict=results_dict, unit_id=unit_id)


class RzCollectionComposer(rottnest_composer.RottnestComposer):
    '''
        Wrapper on the results composer
    '''
    @staticmethod
    def results_composer_constructor():
        return RzCollectionResultsComposer
