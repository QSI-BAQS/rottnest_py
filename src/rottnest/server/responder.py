
import inspect
import json

class Result:

    def __init__(self, pkg):
        """
           Constructor, initialises the fields to defaults
           unless pkg contains a value for: result, message and/or obj 
        """
        self.result = 'ok' if 'result' not in pkg else pkg['result']
        self.message = '' if 'message' not in pkg else pkg['message']
        self.obj = None if 'obj' not in pkg else pkg['obj']
        

    @staticmethod
    def Ok(obj):
        """
           Labels the result as okay, if
           an object of this nature is absent,
           it will use the defaults as part of the
           constructor
        """
        return Result({
                          'result': 'ok',
                          'obj' : obj
                      })
        

    @staticmethod
    def Alt(msgkind, obj):
        """
           Labels the result as Alt,
           used for redirecting and sending
           a different response kind
        """
        return Result({
            'result': 'alt',
            'message': msgkind,
            'obj': obj
        })

    @staticmethod
    def Err(msg):
        """
           Labels the result as Error, if
           an object of this nature is absent,
           it will use the defaults as part of the
           constructor
        """
        return Result({
            'result': 'err',
            'obj': msg 
        })

    def is_ok(self):
        """
            Checks to see if Ok kind
        """
        return self.result == 'ok'

    def is_err(self):
        """
            Checks to see if Error kind
        """
        return self.result == 'err'

    def is_alt(self):
        """
            Checks to see if Alt kind
        """
        return self.result == 'alt'

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

class ResponseValidationException(Exception):
    """
        Exception to outline that the validation on the
        function did not pass.
    """
    pass

class Responder:
    """
       Responder class that is responsible for providing response
       triggers to callers
    """

    EXPFORM_PARAM_COUNT = 3
    EXPFORM_KINDS = [
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.VAR_KEYWORD
    ]

    OUTPUT_FMT_MAP = {
        'JSON': json.dumps
    }
    
    def __init__(self, cfg):
        """
           Initialises the response map, will allow strings (message kinds)
           to be assigned to functions 
        """
        self.response_map = {}
        self.fullqual_resp_map = {}
        self.full_namespace = cfg['full_namespace']
        self.namespace_mask = cfg['namespace_mask']
        self.namespace_prefix = cfg['namespace_prefix']
        self.convert_dots = cfg['convert_dot']
        self.serialization_fn = Responder.OUTPUT_FMT_MAP[cfg['output_fmt']]


    def validate_responsefn(self, responsefn):
        """
           Will check to see if the responsefn function
           added will match the expected form

           Must comply with the form:
           def fn(app, msg, **kwargs)
        """

        fnsig = inspect.signature(responsefn)
        params = fnsig.parameters.values()        
        argcount = len(params)
        
        if argcount != Responder.EXPFORM_PARAM_COUNT:
            return (False, 'Parameter count does not match')

        for (i, p) in enumerate(params):
            if p.kind != Responder.EXPFORM_KINDS[i]:
                return (False, 'Function parameter kind does not meet expected form')
        
        return (True, '')

    def register(self, messagekind=None):
        """
           Registers a response but retrieves the module_name automatically
           Method is intended to be used as a decorator in python

           It will wrap the response in another function as well as
           also wrapping the response object as based on the serialization
           format
        """
        serfmt_fn = self.serialization_fn
        modmask = self.namespace_mask
        def _respwrap(responsefn):
            msgkind = messagekind

            if msgkind is None:
                msgkind = responsefn.__name__
            modname = responsefn.__module__
            full_qualname = '_'.join([modname, msgkind])
            
            def _invoke_wrapper(app, message, **kwargs):
                result = responsefn(app, message, **kwargs)

                payload = {}
                alt_message = False
                
                if isinstance(result, Result):
                      if result.is_alt():
                          alt_message = True
                if alt_message:
                    msg = {
                        'message': result.get_message(),
                        'payload': result.get_obj()
                    }

                    return serfmt_fn(msg)
                else:
                    if result is not None:
                        if isinstance(result, Result):
                            payload = result.get_obj()
                        else:
                            payload = result
                    nfq = full_qualname
                    if not self.full_namespace:
                        nfq = nfq.replace(modmask, '')
                    if self.convert_dots:
                        nfq = nfq.replace('.', '_')
                    msg = {
                        'message': nfq,
                        'payload': payload
                    }

                    return serfmt_fn(msg)
                    
            
            self.register_response(modname, msgkind, _invoke_wrapper)
        return _respwrap

    def register_response(self, module_name, messagekind, responsefn):
        """
           Registers a response to the responder, it will
           accept the module_name, messagekind and response function
        """
        resp_map = {}
        if not self.full_namespace:
            modmask = self.namespace_mask
            module_name = module_name.replace(modmask, '')
        if self.convert_dots:
            module_name = module_name.replace('.', '_')
        if not self.namespace_prefix:
            resp_map = self.response_map
        else:
            if module_name in self.response_map:
                resp_map = self.response_map[module_name]
            else:
                self.response_map[module_name] = resp_map
        (valid, msg) = self.validate_responsefn(responsefn)
        full_qualname = '_'.join([module_name, messagekind])
        if not valid:
            raise ResponseValidationException(msg)
        self.fullqual_resp_map[full_qualname] = responsefn
        resp_map[messagekind] = responsefn


    def retrieve_response(self, module_name, messagekind):
        """
            Retrieves a specific response based on the module_name
            and the message kind.

            Will return None if the entry does not exist
        """
        bindingfn = None
        if module_name in self.response_map:
            if messagekind in self.response_map[module_name]:
                 bindingfn = self.response_map[module_name][messagekind]
        return bindingfn 

    def register_directly(self, fullname, respfn):
        '''
           Allows the direct mapping of a full qualified name
           and the function 
        '''
        self.response_map[fullname] = respfn
        self.fullqual_resp_map[fullname] = respfn

    def retrive_with_fullqual(self, mapkey):
        """
            Uses the fullqualified name to retrieve the
            response function
        """
        bindingfn = None
        if mapkey in self.fullqual_resp_map:
            bindingfn = self.fullqual_resp_map[mapkey]
        return bindingfn 

    def fullqual_map(self):
        """
            Returns the fullqualified name map of the response functions
        """
        return self.fullqual_resp_map

    def response_map(self):
        """
            Returns the responsefn map associated
        """
        return self.response_map


DEFAULT_CONFIG = {
    "full_namespace": False,
    "namespace_mask": ''.join([__name__.replace('responder', ''), 'controller.']),
    "namespace_prefix": True,
    "convert_dot": True,
    "output_fmt": "JSON",
}

responder = Responder(DEFAULT_CONFIG)

