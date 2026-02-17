import json
import unittest

from rottnest.server.util.result import Result

class ResultTypeTests(unittest.TestCase):
    '''
        Ensure that the result type is able to be serialised
        and communicated to the frontend and other components of the
        application 
    '''


    def test_result_ok_serialise(self):
        '''
           Test case will show that Ok is serialisable and usable 
        '''

        res_obj = Result.Ok({})
        res_obj_str = res_obj.serialize(lambda r : json.dumps(r))

        assert res_obj is not None
        assert res_obj_str is not None
        assert isinstance(res_obj_str, str)
         
    def test_result_alternate_serialise(self):
        '''
           Test case will show that Alternate is serialisable and usable 
        '''

        res_obj = Result.Alternate('Alternate Object', {})
        res_obj_str = res_obj.serialize(lambda r : json.dumps(r))

        assert res_obj is not None
        assert res_obj_str is not None
        assert isinstance(res_obj_str, str)
        
    def test_result_err_serialise(self):
        '''
           Test case will show that Err is serialisable and usable 
        '''

        res_obj = Result.Error('An error has occurred')
        res_obj_str = res_obj.serialize(lambda r : json.dumps(r))

        assert res_obj is not None
        assert res_obj_str is not None
        assert isinstance(res_obj_str, str) 
