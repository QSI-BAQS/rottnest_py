'''
    Interface specification for routes 
    This constraints the route binds to the server to those defined  
    By these interface specifications
'''

from .interface_exceptions import (
    NoRoutesException,
    MissingRouteException,
    UndefinedRouteException,
    DuplicateRouteException
)

class RouteInterfaceSpecification:
    '''
        Specifies a set of route route that must be implemented 
        These may be constructed by a class or collection of classes
    '''

    _ROUTE_NAME = '_routes'


    def __init__(self, app, *cons, routes=None):
        '''
            Constructor
            :: app :: Application object to bind routes to 
            :: *cons :: Objects that implement the interface 
        '''
        # Default to kwarg
        # Second to test for a _routes variable
        if (
                # Check that no routes were passed
                (routes is None)
                and # Check that no routes were set as a class variable 
                (routes := getattr(
                    self,
                    self._ROUTE_NAME,
                    routes
                )) is None
            ):

            # No routes defined, raise Exception
            raise NoRoutesException(
                interface=self.__class__
            )

        if len(routes) < 1:
            raise NoRoutesException(
                interface=self.__class__
            )

        self._routes = routes 

        bindings = self.collect_route_bindings(cons)
        #self.bind_routes(app, bindings)

    def collect_route_bindings(self, cons) -> dict: 
        '''
            Collects the route and asserts the completeness of the interface
            :: *cons :: Class constructors implementing a get_route_binds method that in turn
                implement the interface for this specification   

            Returns a dictionary of routes to bindings

            Raises an exception if a route binding is not specified
            Raises an exception if a route binding is not uniquely specified
            Raises an exception if a route binding is specified by the implementation but not the interface  
        '''
        self._binds = {route: None for route in self.get_routes()}

        for constructor in cons:
            for route, fn in constructor.get_routes():

                # Route requested that is not required by interface
                if route not in self._binds:
                    raise UndefinedRouteException(
                        route=route,
                        interface = self.__class__
                    )
                else:
                    # Check route is not already bound
                    if self._binds[route] is not None:
                        raise DuplicateRouteException(
                            route=route,
                            interface = self.__class__
                        )

                    # Bind unbound route
                    self._binds[route] = fn 

        # Check that all routes are bound
        # Return only if all routes are bound uniquely
        for route, fn in self._binds.items():
            if fn is None:
                raise MissingRouteException(
                    route=route,
                    interface = self.__class__
                )

        # Return the bindings
        return self._binds

    def get_routes(self) -> list:
        '''
            Getter wrapper for interface routes
        '''
        return self._routes

    def get_route_binds(self) -> dict:
        return self._binds 
