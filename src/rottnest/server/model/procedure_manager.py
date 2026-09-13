'''
   This is a model object for the procedure manager to allow for
   operations to occur ot be submitted.
   
'''
from rottnest.procedures.procedure_manager import ProcedureManager

def procedure_manager_submit_procedure_sync(procedure):
    '''
       Procedure that will be executed immediately
       Result is sent back after completion
    '''
    procmanager = ProcedureManager.get_instance()
    result = procmanager.execute_immediate(procedure)
    return result


def procedure_manager_submit_procedure_async(procedure):
    '''
       Procedure that will be deferred for execution 
    '''
    procmanager = ProcedureManager.get_instance()
    result = procmanager.execute_defer(procedure)
    return result

def procedure_manager_get_procedure_state(procedure_id):
    '''
       Given a procedure id that the manager
       would have tagged with a integer (pylong)
    '''
    procmanager = ProcedureManager.get_instance()
    result = procmanager.get_procedure_state(procedure_id)
    return result


def procedure_manager_abort_procedure(procedure_id):
    '''
       Given a procedure id, the procedure that is running should be aborted 
    '''
    procmanager = ProcedureManager.get_instance()
    result = procmanager.abort_procedure(procedure_id)
    return { 'procedure_id': procedure_id, issued: True }

def procedure_manager_get_active_procedure_list():
    '''
        Currently set of executing procedures that the manager
        is operating on.
    '''
    procmanager = ProcedureManager.get_instance()
    result = procmanager.get_procedure_table()
    return result
