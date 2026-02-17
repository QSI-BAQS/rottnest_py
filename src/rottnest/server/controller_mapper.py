'''
   Controller mapp is a simple class that will
   build the responses based on each set of api endpoints 
'''

import sys
import json

from collections.abc import Callable
from typing import Self, Any
from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.app.application import RottnestApplication

class ControllerBuilder:
    '''
       Builder of the controllers 
    '''

    def __init__(self, mapper: Any, serializer=json.dumps):
        '''
            Initialises the builder
        '''
        self.mapper = mapper
        self.serializer = serializer


    def attach(self, route_class: type[RouteInterface]) -> Self:
        '''
            Adds another set of routes to the builder    
        '''
        serialize = self.serializer
        routes = route_class.get_routes()

        def __class_route_constructor(route_method: classmethod, route_class: type[RouteInterface]):
            def __route_fn_instance(app: RottnestApplication, message: dict, *args, **kwargs):
                obj = route_method.__func__(route_class, message, **kwargs)
                serial_data = obj.serialize(serialize)
                return serial_data

            return __route_fn_instance
        
        for route_item in routes:
            
            route_method = route_item[1]
            
            route_fn = __class_route_constructor(route_method, route_class)
            
            self.mapper._route_dict[route_item[0]] = route_fn

        return self

    def build(self):
        '''
            Builds the mapper to be used
        '''
        return self.mapper
        

class ControllerMapper:
    '''
       ControllerMapper, uses builder object to
       assemble the mapped object as a result
    '''


    def __init__(self, serialiser=json.dumps):
        '''
           Initialises the controller mapper
           type, holds a dictionary with string to function call 
        '''
        self._route_dict = {}
        self.serialiser = serialiser


    def update_routes(self, routes: 'RouteInterface') -> None:
        '''
           Updates the dictionary with another set of routes 
        '''
        self._route_dict.update(routes)

    def set_serialiser_object(self, serialiser: Callable[[Any], str]) -> None:
        '''
           Sets the serialiser object  
        '''
        self.serialiser = serialiser

    def get_serialiser_object(self) -> Callable[[Any], str]:
        '''
           Gets the serialiser object associated with the mapper 
        '''
        return self.serialiser
    
    def get(self, message: str, err: Callable[[], None]) -> Any:
        '''
           Will get the callback based on the message name itself 
        '''
        if message not in self._route_dict:
            print('Unable to find route function from string', file=sys.stderr)
            return err
        return self._route_dict[message]
    
    @staticmethod
    def assemble() -> ControllerBuilder:
        '''
           Returns the builder for the mapper
           so the routes can be used 
        '''
        mapper = ControllerMapper()
        return ControllerBuilder(mapper, mapper.serialiser)
    
    
