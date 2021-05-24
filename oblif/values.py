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
        if not var in self.dic: raise NameError("name '" + var + "' is not always set")
        if isinstance(self.dic[var], cachedifthenelse): 
#            print("ifthenelsing", var)
#            if self.dic[var].guard is not None: print("* ifthenelse", var, self.dic[var].guard, "?", self.dic[var].ifval, ":", self.dic[var].elseval)
            self.dic[var]=self.dic[var]()
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
    
def apply_to_label(vals, orig):
    if orig is None: return vals
    
    ifguard = vals["__guard"]
    ret = values()
    for nm in orig:
        if nm in vals:
            if (vif:=vals.get(nm)) is (velse:=orig.get(nm)):
                ret[nm] = vif
            else:
                if ifguard is True or ifguard is False or isinstance(ifguard,int):
                    raise RuntimeError("trivial guard")
                ret[nm] = cachedifthenelse(ifguard, vif, velse)

    return ret  

def apply_to_labels(vals, orig1, orig2, cond):
    if cond is True:
        return [apply_to_label(vals, orig1), orig2]
    elif cond is False:
        return [orig1, apply_to_label(vals, orig2)]        
        
    guard = vals["__guard"]
    guard1 = guard&cond
    guard2 = guard&(1-cond)
    
    vals["__guard"] = guard1
    ret1 = apply_to_label(vals, orig1)
    
    if orig1 is None and orig2 is None: vals = vals.copy()
        
    vals["__guard"] = guard2
    ret2 = apply_to_label(vals, orig2)
    
    ret1["__guard"] = guard1  # because may be overwritten to guard2 if we do not copy vals
    
    return [ret1,ret2]

def values_new():
    return values()