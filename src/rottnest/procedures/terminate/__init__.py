from .procedure_terminate_pool import TerminatePoolProcedure 

def execute(args, **kwargs):
    proc = TerminatePoolProcedure(*args, **kwargs)
    proc.execute()
