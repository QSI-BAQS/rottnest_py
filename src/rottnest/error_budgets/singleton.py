'''
    Singleton instance of the error budget
'''

def get_error_budget() -> "ErrorBudget":
    '''
        Getter for the singleton instance
    '''
    from rottnest.plugins import error_budgets
    return error_budgets.get_current_option()

