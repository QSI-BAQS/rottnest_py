'''
    MPSC Channel - Workaround since the compiler_environment is not a full
        tree, only subtree (stages can only access parent, not initiator)
    
'''
from enum import Enum

MPSC_CHANNEL_CAPACITY = 4096 #Objects, not bytes

class MPSCChannelState(Enum):
    '''
       ChannelState is used to provide information regarding
       if the channel has be specified to be created, invalid... etc 
    '''
    INVALID = 0
    CHANNEL_CREATED = 1
    CHANNEL_EXISTS = 2
    CHANNEL_DESTROYED = 3
    READER_CREATED = 4
    READER_EXISTS = 5
    READER_STOPPED = 6
    WRITER_CREATED = 7
    WRITER_STOPPED = 8

    # Used to outlined of the channel is finished or not
    CHANNEL_ACTIVE = 10
    CHANNEL_INACTIVE = 11


class MPSCChannelMessageKind(Enum):
    '''
       Outlines a message kind that cna be used
       for communication 
    '''
    OBJECT = 1
    ITERABLE = 2
    

class MPSCChannelMessage:
    '''
       ChannelMessage is used to create a taggable component that can
       be identified without needing ciruclar referencing 
    '''

    def __init__(self, kind: MPSCChannelMessageKind, data: object):
        '''
           Initialises the channel message 
        '''
        self.data = data
        self.kind = kind

    @classmethod
    def make_object(cls, obj):
        '''
           Makes a message that is a singular object 
        '''
        return MPSCChannelMessage(MPSCChannelMessageKind.OBJECT, obj)

    @classmethod
    def make_iterable(cls, iterable_object):
        '''
            Makes a message that contains an iterable object
        '''
        return MPSCChannelMessage(MPSCChannelMessageKind.ITERABLE, iterable_object)

    def is_iterable(self):
        '''
           Method to outline if it is iterable or not 
        '''
        return self.kind == MPSCChannelMessageKind.ITERABLE

    def get_object(self):
        '''
           Gets the contained object 
        '''
        return self.data

    def get_message_kind(self):
        '''
           Gets the message kind for others to switch on 
        '''
        return self.kind

class MPSCChannel:
    '''
       Multi-Procedure, Single-Consumer channel - Single process only
       This is designed to keep a simple data transfer abstraction away from
       needing to pull singletons/mix them with procedures or other components
       explicitly 
    '''

    def __init__(self, key: str, capacity=MPSC_CHANNEL_CAPACITY):
        '''
           Initialises a MPSC Channel - Will have a reader and writer 
        '''
        self.buffer: list[MPSCChannelMessage] = []
        self.capacity = capacity
        self.length = 0
        self.state = MPSCChannelState.CHANNEL_CREATED


    def get_capacity(self):
        '''
           Gets the capacity of teh buffer itself 
        '''
        return self.capacity

    def get_length(self):
        '''
           Gets the number of elements in the buffer 
        '''
        return self.length


    def enqueue(self, obj: MPSCChannelMessage) -> bool:
        '''
           Enqueues a new object to the buffer 
        '''
        if self.length >= self.capacity:
            return False
        self.buffer.append(obj)
        self.length += 1
        return True

    def dequeue(self) -> MPSCChannelMessage | None:
        '''
           Gets an object from the queue or otherwise None 
        '''
        result = None
        if self.length > 0:
            result = self.buffer.pop(0)
            self.length -= 1
        return result

    def set_state(self, state: MPSCChannelState):
        '''
           Sets the state of the MPSCChannel 
        '''
        self.state = state

    def get_state(self):
        '''
           Gets the state of the MPSCChannel 
        '''
        return self.state

class MPSCReader:
    '''
       Designed to only allow a single consumer
       to retrieve these objects 
    '''

    def __init__(self, mpsc_key: str, mpsc_channel: MPSCChannel):
        '''
           Initialises the MPSCReader to retrieve the data only, no write methods 
        '''
        self.mpsc_key = mpsc_key
        self.mpsc_channel = mpsc_channel
        self.state = MPSCChannelState.READER_CREATED

    def read(self) -> MPSCChannelMessage | None:
        '''
           Gets an object from the channel 
        '''
        if self.state == MPSCChannelState.READER_STOPPED:
            return None
        result = self.mpsc_channel.dequeue()
        return result

    def read_all(self) -> list[MPSCChannelMessage]:
        '''
           Retrieves all messages currently stored in the buffer 
        '''
        data = []
        obj = self.read()

        while obj is not None:
            data.append(obj)
            obj = self.read()

        return data
            
    def message_count(self):
        '''
           Checks to see if the reader has data or not 
        '''
        return self.mpsc_channel.get_length()

    def set_state(self, state: MPSCChannelState):
        '''
           Sets the state of the MPSCChannel 
        '''
        self.state = state

    def get_state(self):
        '''
           Gets the state of the MPSCChannel 
        '''
        return self.state

class MPSCWriter:
    '''
       Designed to only allow a multi producer, since the GIL exists
       it probably isn't much of a problem
    '''

    def __init__(self, mpsc_key: str, mpsc_index: int, mpsc_channel: MPSCChannel):
        '''
           Initialises the MPSCReader to retrieve the data only, no write methods 
        '''
        self.mpsc_key = mpsc_key
        self.mpsc_index = mpsc_index
        self.mpsc_channel = mpsc_channel
        self.state = MPSCChannelState.WRITER_CREATED

    def write(self, obj: object) -> bool:
        '''
           Writes to the mpsc_channel
           if the buffer is full, False will be returned
        '''
        if self.state == MPSCChannelState.WRITER_STOPPED:
            return False
        return self.mpsc_channel.enqueue(MPSCChannelMessage.make_object(obj))


    def write_iter(self, obj: object) -> bool:
        '''
           The object given is assumed to be an iterable object 
        '''
        if self.state == MPSCChannelState.WRITER_STOPPED:
            return False
        return self.mpsc_channel.enqueue(MPSCChannelMessage.make_iterable(obj))

    def set_state(self, state: MPSCChannelState):
        '''
           Sets the state of the MPSCChannel 
        '''
        self.state = state

    def get_state(self):
        '''
           Gets the state of the MPSCChannel 
        '''
        return self.state

class MPSCChannelProvider:
    '''
       MPSCChannelProvider - Is used to construct a channel
       that can be retrieved given a key
       State information is provided on the request of the channel (eiter reading or writing) 
    '''
    _instance = None

    def __init__(self):
        '''
           Simple initialisation - Creates a map of objects for it to be ready
           to use

           It will also ensure that the  
        '''
        self.channel_map: dict[str, MPSCChannel] = dict()
        self.channel_writer_refs: dict[str, list[MPSCWriter]] = dict()
        self.channel_reader_refs: dict[str, MPSCReader] = dict()


    @classmethod
    def get_instance(cls):
        '''
           Gets the singleton instance of the provider 
        '''
        inst = MPSCChannelProvider._instance
        if inst is None:
            inst = MPSCChannelProvider()
            MPSCChannelProvider._instance = inst

        return inst


    def create_channel(self, key: str, silent=False) -> MPSCChannelState:
        '''
           Creates a channel under a key, does not assign reader or writer
           If the channel exists, it will return INVALID 
        '''
        if key in self.channel_map:
            if not silent:
                print(f"Channel '{key}' was exists, a new channel is not being started")
            return MPSCChannelState.CHANNEL_EXISTS

        channel = MPSCChannel(key)
        self.channel_map[key] = channel
        
        return MPSCChannelState.CHANNEL_CREATED
        

    def get_reader(self, key: str) -> tuple[MPSCReader | None, MPSCChannelState]:
        '''
           Given a key, this will be used to retrieve a reader for a channel
           It will return invalid, if the channel doesn't exist
           It will return reader_exists if the channel exists and the reader is used
        '''
        if key not in self.channel_map:
            print(f"Channel '{key}' does not exist")
            return (None, MPSCChannelState.INVALID)

        if key in self.channel_reader_refs:
            print(f"Reader for Channel '{key}' exists, you cannot acquire a new one")
            return (None, MPSCChannelState.READER_EXISTS)
            
        
        channel = self.channel_map[key]
        
        if channel.get_state() is MPSCChannelState.CHANNEL_DESTROYED:
            print(f"Channel '{key}' was destroyed, is not being recreated")
            return (None, MPSCChannelState.CHANNEL_DESTROYED)
        
        reader = MPSCReader(key, channel)
        self.channel_reader_refs[key] = reader
        
        return (reader, MPSCChannelState.READER_CREATED)


    def get_writer(self, key: str) -> tuple[MPSCWriter | None, MPSCChannelState]:
        '''
           Gets the writer end, if the channel does not exist, it will return None and invalid
           otherwise it will create a writer for the channel 
        '''
        if key not in self.channel_map:
            return (None, MPSCChannelState.INVALID)
        
        channel = self.channel_map[key]

        if channel.get_state() is MPSCChannelState.CHANNEL_DESTROYED:
            print(f"Channel '{key}' was destroyed, is not being recreated")
            return (None, MPSCChannelState.CHANNEL_DESTROYED)

        if key not in self.channel_writer_refs:
            self.channel_writer_refs[key] = list()

        
        new_writer_indx = len(self.channel_writer_refs[key])
        
        writer = MPSCWriter(key, new_writer_indx, channel)

        self.channel_writer_refs[key].append(writer)
        
        return (writer, MPSCChannelState.WRITER_CREATED)

    def close_reader(self, reader_object: MPSCReader) -> MPSCChannelState:
        '''
           When given a  reader object, it will attempt to close it
        '''
        key = reader_object.mpsc_key
        if key not in self.channel_map:
            return MPSCChannelState.INVALID

        if key not in self.channel_reader_refs:
            return MPSCChannelState.INVALID

        reader_object.set_state(MPSCChannelState.READER_STOPPED)

        return MPSCChannelState.READER_STOPPED


    def close_writer(self, writer_object: MPSCWriter):
        '''
           When given a writer object, we will attempt to close it 
        '''
        key = writer_object.mpsc_key
        if key not in self.channel_map:
            return MPSCChannelState.INVALID

        if key not in self.channel_reader_refs:
            return MPSCChannelState.INVALID
        
        writer_object.set_state(MPSCChannelState.WRITER_STOPPED)

        return MPSCChannelState.WRITER_STOPPED

    def close_channel(self, channel_key: str) -> MPSCChannelState:
        '''
           Closes the channel and will update the readers and writers that hold
           a reference to it 
        '''
        
        if channel_key not in self.channel_map:
            return MPSCChannelState.INVALID

        channel = self.channel_map[channel_key]
        reader = self.channel_reader_refs[channel_key]
        writers = self.channel_writer_refs[channel_key]

        reader.set_state(MPSCChannelState.READER_STOPPED)
        for w in writers:
            w.set_state(MPSCChannelState.WRITER_STOPPED)

        channel.set_state(MPSCChannelState.CHANNEL_DESTROYED)

        # Will now clean up
        del self.channel_reader_refs[channel_key]
        del self.channel_writer_refs[channel_key]
        del self.channel_map[channel_key]

        return MPSCChannelState.CHANNEL_DESTROYED

    def recreate_channel(self, key: str) -> MPSCChannelState:
        '''
            Recreates the channel, even if it exists or not
            WARNING: This may leave orphan readers and writers
                These will do nothing when used
        '''
        self.close_channel(key)
        return self.create_channel(key, silent=True)
