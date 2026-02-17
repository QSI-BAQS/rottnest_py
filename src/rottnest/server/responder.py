'''
    TODO: Marked for removal
    Responder object
    Handles communication with the websocket
'''

from rottnest.server.util.result import Result
import inspect
import json

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
        self.response_map: dict = {}
        self.fullqual_resp_map = {}
        self.full_namespace = cfg['full_namespace']
        self.namespace_mask = cfg['namespace_mask']
        self.namespace_prefix = cfg['namespace_prefix']
        self.convert_dots = cfg['convert_dot']
        self.serialization_fn = Responder.OUTPUT_FMT_MAP[cfg['output_fmt']]

    def validate_responsefn(self, response_fn):
        """
           Will check to see if the responsefn function
           added will match the expected form

           Must comply with the form:
           def fn(app, msg, **kwargs)
        """

        fn_sig = inspect.signature(response_fn)
        params = fn_sig.parameters.values()        
        argcount = len(params)
       
        # Check if number of paramaters match 
        if argcount != Responder.EXPFORM_PARAM_COUNT:
            return (False, 'Parameter count does not match')

        # Check if parameter type matches 
        for (i, p) in enumerate(params):
            if p.kind != Responder.EXPFORM_KINDS[i]:
                return (False, 'Function parameter kind does not meet expected form')
        
        return (True, '')

    def register(self, message_kind=None):
        """
           Registers a response but retrieves the module_name automatically
           Method is intended to be used as a decorator in python

           It will wrap the response in another function as well as
           also wrapping the response object as based on the serialization
           format
        """

        modmask = self.namespace_mask
        def _respwrap(responsefn):
            msg_kind = message_kind

            if msg_kind is None:
                msg_kind = responsefn.__name__
            modname = responsefn.__module__
            full_qualname = '_'.join([modname, msg_kind])
            
            def _invoke_wrapper(app, message, **kwargs):
                result = responsefn(app, message, **kwargs)

                payload = {}
                alt_message = False
                
                if isinstance(result, Result):
                      if result.is_alt():
                          alt_message = True
                if alt_message:
                    msg = {
                        Result.MESSAGE: result.get_message(),
                        Result.PAYLOAD: result.get_obj()
                    }

                    return self.serialization_fn(msg)
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
                        Result.MESSAGE: nfq,
                        Result.PAYLOAD: payload
                    }

                    return self.serialization_fn(msg)
            
            self.register_response(modname, msg_kind, _invoke_wrapper)
        return _respwrap

    def register_response(self, module_name, message_kind, responsefn):
        """
           Registers a response to the responder, it will
           accept the module_name, message_kind and response function
        """
        resp_map = {}
        if not self.full_namespace:
            modmask = self.namespace_mask
            module_name: str = module_name.replace(modmask, '')

        if self.convert_dots:
            module_name: str = module_name.replace('.', '_')

        if not self.namespace_prefix:
            resp_map = self.response_map
        else:
            if module_name in self.response_map:
                resp_map = self.response_map[module_name]
            else:
                self.response_map[module_name] = resp_map
        (valid, msg) = self.validate_responsefn(responsefn)
        full_qualname = '_'.join([module_name, message_kind])
        if not valid:
            raise ResponseValidationException(msg)
        self.fullqual_resp_map[full_qualname] = responsefn
        resp_map[message_kind] = responsefn

    def retrieve_response(self, module_name, message_kind):
        """
            Retrieves a specific response based on the module_name
            and the message kind.

            Will return None if the entry does not exist
        """
        bindingfn = None
        if module_name in self.response_map:
            if message_kind in self.response_map[module_name]:
                 bindingfn = self.response_map[module_name][message_kind]
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


# I feel like this is basically pointless
DEFAULT_CONFIG = {
    "full_namespace": False,
    "namespace_mask": ''.join([__name__.replace('responder', ''), 'controller.']),
    "namespace_prefix": True,
    "convert_dot": True,
    "output_fmt": "JSON",
}

responder = Responder(DEFAULT_CONFIG)

