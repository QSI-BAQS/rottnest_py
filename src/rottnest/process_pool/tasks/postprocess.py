'''
    Simple ping task
'''
from rottnest.compute_units.layout_proxy import LayoutProxy

from rottnest.process_pool import commands, symbols
from .pool_task import PoolTask

class GetPostprocessorParametersTask(PoolTask):
    '''
        Sets a plugin module option
    '''
    EXPECT_RESPONSE = True

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.GET_POSTPROCESSOR_PARAMETERS

    def task(
            self,
            pool_manager: "PoolManager",
            *args,
            **kwargs
    ):
        postprocessor = pool_manager.composer.get_postprocessor()
        print("POST: ", type(postprocessor))

        return postprocessor.get_current_parameters()

class SetPostprocessorParametersTask(PoolTask):
    '''
        Rebuilds the postprocessor from parameters 
    '''

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.SET_POSTPROCESSOR_PARAMETERS

    def task(
            self,
            pool_manager: "PoolManager",
            parameters,
            *args,
            **kwargs
    ):
        return pool_manager.composer.build_postprocessor(**parameters)


class RunPostprocessorTask(PoolTask):
    '''
        Sets a plugin module option
    '''
    EXPECT_RESPONSE = True

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.RUN_POSTPROCESSOR

    def task(
            self,
            pool_manager: "PoolManager",
            *args,
            **kwargs
    ):
        postprocessor = pool_manager.composer.get_postprocessor()
        layouts = LayoutProxy.get_layouts()
        postprocessor.set_layouts(layouts)

        result = pool_manager.composer.get_result().to_runchart()
        postprocessor.set_result(result)
    
        print("POST: ", type(postprocessor))

        # Runs the postprocessor
        return postprocessor()

