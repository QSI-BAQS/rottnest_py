'''
    Tests pool process
'''
import unittest
import random

from rottnest.procedures.option_setters.error_budget_setters import SetErrorBudgetProcedure 

from rottnest.error_budgets import get_error_budget 


class ErrorBudgetTest(unittest.TestCase):

    def test_set_error_budget(self):

        # Going to do direct comparison of floats
        # Just to prove identity
        p_phys = 1 / random.randint(int(1e3), int(1e5))
        err = 1 / random.randint(int(1e3), int(1e5))


        proc = SetErrorBudgetProcedure(p_phys=p_phys, target_error=err)
        proc.execute()

        err_obj = get_error_budget()
        assert err_obj.get_p_physical() == p_phys
        assert err_obj.get_target_error() == err


if __name__ == '__main__':
    tst = ErrorBudgetTest()
    tst.test_set_error_budget()
    #unittest.main()

