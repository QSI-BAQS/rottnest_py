from .interface_exceptions import DuplicateRouteException
'''
    Routes metaclass
'''
class Routes(type):
    '''
        Singleton route collector
        This is metaclassed to separate route contexts
        on a per-subclass basis
    '''

    _ROUTES = '_routes'
    _routes = {}

    @classmethod
    def add_route(cls, route, fn):
        '''
            Adds unique routes
        '''
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

    @classmethod
    def get_routes(cls):
        '''
            Gets the routes for this class object
        '''
        return cls._routes.items()

    def bind_route(route):
        '''
            Via the magic of metaclassing the 
            target route object is uniqe for each
            class instance
        '''
        def _wrap(fn): 
            Routes.add_route(route, fn)
            return fn 
        return _wrap

