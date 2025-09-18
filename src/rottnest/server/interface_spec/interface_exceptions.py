'''
    Defines exceptions raised by the interface
'''

class MissingRouteException(Exception):
    '''
        Missing route exception
    '''

    _MISSING_ROUTE = "Route {route} is not defined by interface {interface}"

    def __init__(self, route, interface):
        return super().__init__(
            self._MISSING_ROUTE.format(
                route=route,
                interface=interface
            )
        )


class UndefinedRouteException(Exception):
    '''
        Undefined route exception
    '''

    _UNDEFINED_ROUTE = "Route {route} requested but does not exist in interface {interface}"

    def __init__(self, route, interface):
        return super().__init__(
            self._UNDEFINED_ROUTE.format(
                route=route,
                interface=interface
            )
        )
   

class DuplicateRouteException(Exception):
    '''
        Duplicate route exception
    '''

    _DUPLICATE_ROUTE = "Route {route} has duplicate definitions in interface {interface}"

    def __init__(self, route, interface):
        return super().__init__(
            self._DUPLICATE_ROUTE.format(
                route=route,
                interface=interface
            )
        )
  

class NoRoutesException(Exception):
    '''
        No Routes defined exception
    '''

    _NO_ROUTES = "Interface {interface} has no routes defined"

    def __init__(self, interface):
         return super().__init__(
           self. _NO_ROUTES.format(
                interface=interface
            )
        )
 
