import unittest

from rottnest.plugins import error_budgets

class TestErrorBudgets(unittest.TestCase):
  
    def default_budget(self):
        from rottnest_error_budgets.error_budgets.even_distribution import EvenDistribution
        key = EvenDistribution.get_name()
        return key
 
    def test_plugin_load(self):
        '''
            Test that we can load and set the error budget
        '''
        error_budgets.set_current_option(self.default_budget()) 


    def test_options(self):
        '''
            Simple test to see if the key loads correctly
        '''
        key = self.default_budget()
        assert key in error_budgets.get_options()

    def test_option_keys(self):
        key = self.default_budget()
        assert key in error_budgets.get_option_keys()

    def test_default_params(self):

        assert len(error_budgets.get_parameters()) == 0
        error_budgets.set_current_option(self.default_budget()) 
        assert len(error_budgets.get_parameters()) == 2


