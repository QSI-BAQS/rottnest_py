'''
   This is a model object for the procedure manager to allow for
   operations to occur ot be submitted.
   
'''
from rottnest.procedures.procedure_manager import ProcedureManagerSelector

def procedure_manager_submit_procedure_sync(procedure):
    '''
       Procedure that will be executed immediately
       Result is sent back after completion
    '''
    procmanager = ProcedureManagerSelector.get_instance().get_default()
    result = procmanager.execute_immediate(procedure)
    return result


def procedure_manager_submit_procedure_async(procedure):
    '''
       Procedure that will be deferred for execution 
    '''
    procmanager = ProcedureManagerSelector.get_instance().get_default()
    result = procmanager.execute_defer(procedure)
    return result


def get_procedure_state(procedure_id):
    '''
       Given a procedure id that the manager
       would have tagged with a integer (pylong)
    '''
    obj = {
        "procedure_id": None,
        "error" : "Procedure Id is not in the active list" 
    }

    procmanager = ProcedureManagerSelector.get_instance().get_default()
    result = procmanager.get_procedure(procedure_id)
    if result is not None:
        obj = result
        
    return obj

def get_procedure_table():
    '''
        Gets the list of active procedures that are part
        of the procedure manager
    '''
    procmanager = ProcedureManagerSelector.get_instance().get_default()
    result = procmanager.get_procedure_table()
    return result

def abort_procedure(procedure_id):
    '''
       Given a procedure id, the procedure that is running should be aborted 
    '''
    procmanager = ProcedureManagerSelector.get_instance().get_default()
    result = procmanager.abort_procedure(procedure_id)
    if result is not None:
        return { 'procedure_id': procedure_id, 'issued': True }
    else:
        return { 'procedure_id': None, 'issued': False }
