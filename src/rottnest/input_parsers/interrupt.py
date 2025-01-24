class INTERRUPT:
    def __iter__(self):
        yield self 

    def __hash__(self):
        return id(INTERRUPT)

    def __eq__(self, other):
        return hash(self) == hash(other) 
