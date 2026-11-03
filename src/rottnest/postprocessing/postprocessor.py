
import json

from enum import Enum
from geventwebsocket.websocket import WebSocket
from rottnest.server.protocol.net import RottnestPacketBuilder, Rottnest

class PostProcessingAction(Enum):
    '''
       PostProcessingAction
       Will outline what kind of action has occurred 
    '''
    NoAction = 0
    Added = 1
    Replaced = 2
    Removed = 3
    Cleared = 4
    

class PostProcessingEntry:
    '''
       PostProcessingEntry that will hold the fields
       When another subsystem sends data to it 
    '''

    def __init__(self, key: str, origin: str, kind: str, message: str, aggregate=None):
        '''
           Initialises the mesage
        '''
        self.key = key
        self.origin = origin
        self.kind = kind
        self.message = message
        self.aggregate = aggregate

    def to_dict(self) -> dict[str, str | object]:
        '''
           Transform the object to a dict 
        '''

        return {
            'key': self.key,
            'kind': self.kind,
            'origin' : self.origin,
            'message': self.message,
            'aggregate': self.aggregate
        }


    def to_json(self) -> str:
        '''
            Takes the data and prepares it to be packaged
            to be sent to the frontend
        '''

        return json.dumps(self.to_dict())


    def to_message(self) -> dict[str, str]:
        '''
           Transform the object to a dict that is designed to be sent
           to the frontend 
        '''
        packet = RottnestPacketBuilder.message(Rottnest.postprocessing.entry)\
                                        .set_payload(self.to_dict()).build()

        return packet
    

class PostProcessorRegistry:
    '''
       PostProcessorRegistry
       This is used to maintain a dictionary of active entries and
       synchronise on request or ac./server/websocket/websocket_operations/operations_common.pytively with the client 
    '''

    def __init__(self):
        '''
           PostProcessorRegistry init - Will intialise the registry
           and prepare the data to be given or deregistered if needed 
        '''

        self.entries: dict[str, PostProcessingEntry] = dict()


    def get_entries(self) -> dict[str, PostProcessingEntry]:
        '''
            Will return the list of entries
        '''
        return self.entries


    def add_entry(self, entry: PostProcessingEntry) -> PostProcessingAction:
        '''
           Will add an entry to the registry, if the entry exists, it will replace it
        '''
        action = PostProcessingAction.Added
        key = entry.key
        
        if key in self.entries:
            action = PostProcessingAction.Replaced
        
        self.entries[key] = entry

        return action

    def remove_entry(self, key: str) -> PostProcessingAction:
        '''
           Will remove the entry if it exists from the post processing registry 
        '''
        action = PostProcessingAction.NoAction

        if key in self.entries:
            action = PostProcessingAction.Removed
            del self.entries[key]

        return action


    def clear_entries(self):
        '''
           Clears the entries that have been built up 
        '''
        self.entries = dict()

        return PostProcessingAction.Cleared
        
        

class PostProcessorManager:
    '''
       PostProcessorManager, single instance that is able to be
       retrieved by other modules.

       Objects in other subsystems can send messages to this manager.

            Messages must contain:
                * key       - Key identifier that allows us to check for uniqueness
                * origin    - Where the message stems from
                * kind      - What kind of message it is, this is akin to a type
                * message   - The details of the message
                * aggregate - For multiple entries under the same key 
                
    '''
    instance: "PostProcessorManager | None" = None

    def __init__(self):
        '''
            Initialises the post processor manager
        '''
        self.registry = PostProcessorRegistry()

    @classmethod
    def get_instance(cls) -> 'PostProcessorManager':
        '''
           Gets an instance of the postprocessor manager 
        '''
        if cls.instance is None:
            cls.instance = PostProcessorManager()

        return cls.instance

    def get_registry(self) -> PostProcessorRegistry:
        '''
           Gets the registry associated
        '''
        return self.registry

    def add_entry(self, entry: PostProcessingEntry) -> PostProcessingAction:
        '''
           Wrapper around the registry method 
        '''
        return self.registry.add_entry(entry)
    
    def remove_entry(self, key: str) -> PostProcessingAction:
        '''
           Wrapper around the registry method 
        '''
        return self.registry.remove_entry(key)

    def add_and_send_entry(self, websocket: WebSocket, entry: PostProcessingEntry) -> PostProcessingAction:
        '''
           Will send data immediately as it is entered to the registry 
        '''
        message = entry.to_message()
        websocket.send(message)
        return self.registry.add_entry(entry)
    
    def send_all(self, websocket: WebSocket):
        '''
           Will all the entries to the client
        '''
        entries = self.registry.get_entries()
        items = []
        for (_, value) in entries.items():
            items.append(value.to_dict())

        packet = RottnestPacketBuilder.message(Rottnest.postprocessing.all)\
                                .set_payload(items).build()

        websocket.send(packet)
