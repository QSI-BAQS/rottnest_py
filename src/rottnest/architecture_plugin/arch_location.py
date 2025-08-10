from enum import Enum

class ArchLocationKind(Enum):
    '''
       Location Kind, it outlines what kind of
       plugin it is and how that it is held within rottnest 
    '''
    FilePath = 1
    ModuleKey = 2

    def equals(self, a):
        return self.name == a

    def to_name(self):
        return self.name

