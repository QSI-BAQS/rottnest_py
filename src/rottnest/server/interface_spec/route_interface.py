'''
    Routes metaclass
'''
from typing import Callable

from .interface_spec import ROTTNEST_PREFIX
from .interface_exceptions import DuplicateRouteException


class Routes(type):
    '''
        Singleton route collector
        This is metaclassed to separate route contexts
        on a per-subclass basis
    '''

    _ROUTES = '_routes'
    _routes = {}
    _prefixed_routes = {}

    _rottnest_prefix = ROTTNEST_PREFIX 

    @classmethod
    def add_route(cls, module_prefix, route, fn):
        '''
            Adds unique routes
        '''
        # Prepend module
        route = f"{cls._rottnest_prefix}.{module_prefix}.{route}"

        if cls._routes.get(route, None) is not None: 
            raise DuplicateRouteException(interface=cls, route=route)
        cls._routes[route] = fn

    @classmethod
    def __prepare__(metacls, name, bases):
        '''
            Prepares a route dict object for the subclass
            This gets caught between the instantiation of
            the metaclass prepare, class parsing and new 
        '''
        Routes._routes = {} 
        return dict() 

    def __new__(cls, name, bases, classdict):
        '''
            Instance constructor for the class object
        '''
        obj = type.__new__(cls, name, bases, classdict)
        obj._routes = Routes._routes 

        # Reset the dict
        Routes._routes = {}
        return obj


class RouteInterface(metaclass=Routes):
    '''
        Interface parent class
        Metaclassed to hook route aggregation
    '''

    PAYLOAD = 'payload'

    @classmethod
    def get_routes(cls):
        '''
            Gets the routes for this class object
        '''
        return cls._routes.items()

    def bind_route(prefix: str, route: str) -> Callable:
        '''
            Via the magic of metaclassing the 
            target route object is uniqe for each
            class instance
        '''
        def _wrap(fn): 
            Routes.add_route(prefix, route, fn)
            return fn 
        return _wrap

    @staticmethod
    def load(message):
        '''
        Wraps the payload unloader avoiding messy strings
        '''
        return message[Routes.PAYLOAD]

    @staticmethod
    def load_and_model_call(message, field, model_function):
        '''
            Fills a common pattern of loading and calling 
            to a model function with a simple param
        '''
        msg = self.load(message)
        var = msg[field]
        return model_function(field)
