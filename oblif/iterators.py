from .values import apply_to_label, values_new

class IteratorWrapper:
    def __init__(self, it):
        self.it = it
    def __next__(self):
        try:
            return (True,self.it.__next__())
        except:
            return (False,None)

class ObliviousIterator: pass

class ObliviousRange(ObliviousIterator):
    def __init__(self, start, maxi, maxo, step):
        self.start = int(start)
        self.step = int(step)
        self.maxi = maxi
        self.maxo = maxo
        self.cur = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.cur is None:
            if (self.maxi is not None and self.start>=self.maxi): return (False,None)
            self.cur = self.start
            return (True,self.cur)
        
        if self.maxi is not None and self.cur+self.step>=self.maxi: return (False,None)
            
        docont = 1
        for i in range(self.cur+1, self.cur+self.step+1):
            docont &= (i!=self.maxo)
        self.cur += self.step
        return (docont, self.cur)
            
def orange_(minv, max1, max2, step):
    try:
        maxi = None if max1 is None else int(max1)
        try:
            maxo = int(max2)
            return range(minv, min(max1,max2), step)
        except:
            maxo = max2
    except:
        try:
            maxi = max2 if max2 is None else int(max2)
            maxo = max1
        except:
            raise RuntimeError("at least one of the loop bounds must be None or support int()")
    
    return ObliviousRange(minv, maxi, maxo, step)
        
def orange(*args):
    if len(args)==1:
        return orange_(0, args[0][0], args[0][1], 1)
    elif len(args)==2:
        return orange_(args[0], args[1][0], args[1][1], 1)
    elif len(args)==3:
        return orange_(args[0], args[1][0], args[1][1], args[2])
    else:
        raise RuntimeError("wrong number of arguments to range()")
    