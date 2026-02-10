'''
   Controller mapp is a simple class that will
   build the responses based on each set of api endpoints 
'''

import sys
import json

class ControllerBuilder:
    '''
       Builder of the controllers 
    '''

    def __init__(self, mapper, serializer=json.dumps):
        '''
            Initialises the builder
        '''
        self.mapper = mapper
        self.serializer = serializer


    def attach(self, route_class):
        '''
            Adds another set of routes to the builder    
        '''
        serialize = self.serializer
        routes = route_class.get_routes()

        def __class_route_constructor(route_method, route_class):
            def __route_fn_instance(app, message, *args, **kwargs):
                obj = route_method.__func__(route_class, message, **kwargs)
                print(obj.items())
                serial_data = serialize(dict(obj.items()))
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


    def __init__(self):
        '''
           Initialises the controller mapper
           type, holds a dictionary with string to function call 
        '''
        self._route_dict = {}


    def update_routes(self, routes):
        '''
           Updates the dictionary with another set of routes 
        '''
        self._route_dict.update(routes)

    def get(self, message, err):
        '''
           Will get the callback based on the message name itself 
        '''
        if message not in self._route_dict:
            print('Unable to find route function from string', file=sys.stderr)
            return err
        return self._route_dict[message]
    
    @staticmethod
    def assemble():
        '''
           Returns the builder for the mapper
           so the routes can be used 
        '''
        mapper = ControllerMapper()
        return ControllerBuilder(mapper)
    
    
