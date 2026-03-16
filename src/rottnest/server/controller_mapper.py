'''
   Controller mapp is a simple class that will
   build the responses based on each set of api endpoints 
'''
import json
import os

from responder import responder
from collections.abc import Callable
from typing import Self, Any
from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.app.application import RottnestApplication

ControllerMessageKey = 'message'
ControllerPayloadKey = 'payload'

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
                serial_data = obj.serialize_with_tags([('message', message['message'])],\
                                                       'payload', serialize)
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


    def __init__(self, serialiser=json.dumps, respondhandler=None):
        '''
           Initialises the controller mapper
           type, holds a dictionary with string to function call 
        '''
        self._route_dict: dict = {}
        self.serialiser = serialiser
        if respondhandler is None:
            self.responder = responder
        else:
            self.responder = respondhandler

    @staticmethod
    def package_result(message_kind, serialized_data):
        '''
           Repackages the data to enclose it within frontend expected object 
        '''
        return {
            ControllerMessageKey: message_kind,
            ControllerPayloadKey: serialized_data
        }

    def update_routes(self, routes: 'RouteInterface') -> None:
        '''
           Updates the dictionary with another set of routes 
        '''
        self._route_dict.update(routes) #ty: ignore

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

           Uses a responder object to search for legacy endpoints 
        '''
        respfn = err
        if message not in self._route_dict:
            if self.responder is not None:
                resobj = self.responder.retrieve_with_fullqual(message)
            if resobj is not None:
                 respfn = resobj
        else:
            respfn = self._route_dict[message]
        return respfn 
    
    @staticmethod
    def assemble(responder: Any = None) -> ControllerBuilder:
        '''
           Returns the builder for the mapper
           so the routes can be used 
        '''
        mapper = ControllerMapper(respondhandler=responder)
        return ControllerBuilder(mapper, mapper.serialiser)
    
    
