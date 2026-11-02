'''
    Factory for single stage procedures
    Basically just a simple type promotion
'''
from rottnest.procedures import procedure


class _SingleStageProcedure(
    procedure.RottnestCompilerProcedure
):
    '''
        Abstract procedure
        While base stage is not defined, this class is incomplete
        Complete instances are constructed using the SingleStageProcedure factory
    '''
    BASE_STAGE = None
    TAG = None

    def __init__(
            self,
            *args,
            tag = None,
            dependencies = None,
            **kwargs
        ):
        '''
            Base Constructor
        '''
        if self.BASE_STAGE is None:
            raise NotImplementedError(
                "Abstract _SingleStageProcedure used without initialisation"
            )
        instantiated_stage = self.BASE_STAGE(
            *args,
            **kwargs
        )

        super().__init__(
            None,
            stages=[instantiated_stage],
            tag=tag,
            dependencies=dependencies
        )


def SingleStageProcedure(
        name: str,
        tag: str,
        stage: "RottnestCompilerStage"
    ):
        '''
            Factory method wrapping the abstract base stage 
        '''
        return type(name, (_SingleStageProcedure,), {"TAG": tag, "BASE_STAGE": stage})
