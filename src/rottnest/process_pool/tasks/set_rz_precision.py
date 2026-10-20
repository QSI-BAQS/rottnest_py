'''
    Module Synchronisation Command
'''
from .pool_task import PoolTask

from rottnest.process_pool import commands
from rottnest.priority_process import commands as priority_commands

from rottnest.procedures.decomposition_patchers import DecompositionPatchProcedure
from rottnest.procedures.option_setters.procedure_set_option import SetOptionProcedure

from rottnest.rz_decomposer import get_rz_precision, set_rz_precision


class SetRzPrecisionTask(PoolTask):
    '''
        Sets a plugin module option
    '''

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.SET_RZ_PRECISION

    @classmethod
    def submit(
            cls,
            *args,
            **kwargs
        ):
        '''
            Gets and synchronises the rz precision
        '''
        rz_precision: int = get_rz_precision()
        return super().submit(rz_precision)

    def task(
            self,
            pool_manager: "PoolManager",
            rz_precision: int,
            *args,
            **kwargs
    ):
        '''
            Sets the Rz precision on the pool manager
        ''' 
        set_rz_precision(rz_precision)

