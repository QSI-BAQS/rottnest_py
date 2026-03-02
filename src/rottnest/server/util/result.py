import json
from typing import Callable

class Result:
    '''
        Response wrapper object
        Wraps responses to the front end
    '''

    # Constants for message fields
    RESULT = 'result'
    MESSAGE = 'message'
    PAYLOAD = 'payload'
    OBJ = 'obj'
   
    # Message types 
    OK = 'ok'
    ERROR = 'err'
    ALTERNATIVE = 'alt'

    def __init__(self, pkg):
        """
           Constructor, initialises the fields to defaults
           unless pkg contains a value for: result, message and/or obj 
        """
        self.result = Result.OK if Result.RESULT not in pkg else pkg[Result.RESULT]
        self.message = '' if Result.MESSAGE not in pkg else pkg[Result.MESSAGE]
        self.obj = None if Result.OBJ not in pkg else pkg[Result.OBJ]


    @staticmethod
    def auto(result_kind=OK, result_msg=''):
        '''
           Automatically wraps the function/method with a result 
        '''
        # TODO: Complete this method
        def _fn_capture(func: Callable):
            '''
               Capturing a function from controller 
            '''
            def _re_wrapped(cls, message, **kwargs):
                '''
                   Re-wrapped controller 
                '''
                result = None
                try:
                    result = func(cls, message, kwargs)
                    if not isinstance(result, Result):
                        if result_kind == Result.OK:
                            result = Result.Ok(result)
                        else:
                            result = Result.Alternate(result_msg,
                                                      result)
                        
                except Exception as be:
                    result = Result.Error(str(be))


            return _re_wrapped
        return _fn_capture

    @staticmethod
    def Ok(obj):
        """
           Labels the result as okay, if
           an object of this nature is absent,
           it will use the defaults as part of the
           constructor
        """
        return Result({
                          Result.RESULT: Result.OK,
                          Result.OBJ : obj
                      })
        

    @staticmethod
    def Alternate(msg_kind, obj):
        """
           Labels the result as Alt,
           used for redirecting and sending
           a different response kind
        """
        return Result({
            Result.RESULT: Result.ALTERNATIVE,
            Result.MESSAGE: msg_kind,
            Result.OBJ: obj
        })

    @staticmethod
    def Error(msg):
        """
           Labels the result as Error, if
           an object of this nature is absent,
           it will use the defaults as part of the
           constructor
        """
        return Result({
            Result.RESULT: Result.ERROR,
            Result.OBJ: msg 
        })

    def is_ok(self):
        """
            Checks to see if Ok kind
        """
        return self.result == Result.OK

    def is_err(self):
        """
            Checks to see if Error kind
        """
        return self.result == Result.ERROR

    def is_alt(self):
        """
            Checks to see if Alt kind
        """
        return self.result == Result.ALTERNATIVE

    def get_obj(self):
        """
            Getter for the object
        """
        return self.obj

    def get_message(self):
        """
            Getter for the result message, for
            Alt types specifically
        """
        return self.message

    def serialize(self, serialiser):
        '''
            Transforms the object to a dictionary that would
            allow it to be serialisable. 
        '''
        return serialiser(self.obj)


