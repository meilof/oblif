from copy import deepcopy

class cachedifthenelse:
    def __init__(self, guard, ifval, elseval):
        self.guard = guard
        self.ifval = ifval
        self.elseval = elseval
        self.val = None
        
    def get(self):
        return self.val if self.guard is None else self
    
    def __call__(self):
#        print("calling ifelse on", self.guard, self.ifval, self.elseval)
        if self.guard is not None:
            if isinstance(self.ifval,cachedifthenelse): self.ifval = self.ifval()
            if isinstance(self.elseval,cachedifthenelse): self.elseval = self.elseval()
            self.val = self.guard.if_else(self.ifval, self.elseval)
            self.guard = None
            self.ifval = None
            self.elseval = None
        return self.val
        
class values:
    def __init__(self):
        self.dic = {}
        
    def __getitem__(self, var):
        if isinstance(self.dic[var], cachedifthenelse): self.dic[var]=self.dic[var]()
        return self.dic[var]
    
    def get(self, var):
        if isinstance(self.dic[var], cachedifthenelse): 
            return self.dic[var].get()
        else:
            return self.dic[var]        
    
    def __setitem__(self, var, val):
        self.dic[var] = val
        
    def __delitem__(self, var):
        del self.dic[var]
        
    def __iter__(self):
        return self.dic.__iter__()
        
    def clear(self):
        self.dic = {}
        
    def copy(self):
        ret = values()
        ret.dic = dict(self.dic)
        return ret
        
    def __repr__(self):
        return repr(self.dic)
    
def apply_to_label(orig, vals, cond):
#    print("applying to label", orig, vals, cond)
#    print("applying to label")
    if cond is False:
#        print("returning orig")
        return orig
    elif orig is None:
        if cond is True:
#            print("returning vals")
            return vals
        else:
#            print("copying vals")
            ret = vals.copy()
            ret["__guard"] &= cond
            return ret
    else:
#        print("doing ifthenselse", )
        #print("doing ifthenelse", "orig", orig["__guard"], "vals", vals["__guard"], "cond", cond)
        ret = values()
        ifguard = vals["__guard"] & cond
        for nm in orig:
            if nm in vals:
                if (vif:=vals.get(nm)) is (velse:=orig.get(nm)):
                    ret[nm] = vif
                else:
                    if ifguard is True or ifguard is False or isinstance(ifguard,int):
                        raise RuntimeError("trivial guard")
                    ret[nm] = cachedifthenelse(ifguard, vif, velse)
        ret["__guard"] |= ifguard
        return ret

def values_new():
    return values()