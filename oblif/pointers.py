refcounts = {}

class roptr:
    def __init__(obj):
        self.obj = obj
    
    def __del__(self):
        refcounts[id(self.obj)] -= 1
        
        
class rwptr:
    def __init__(obj):
        self.obj = obj
    
    def __del__(self):
        refcounts[id(self.obj)] -= 1
        