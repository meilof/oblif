from copy import deepcopy

#class cachedifthenelse:
#    def __init__(self, guard, ifval, elseval):
#        self.guard = guard
#        self.ifval = ifval
#        self.elseval = elseval
#        self.val = None
#        
#    def get(self):
#        return self.val if self.guard is None else self
#    
#    def __call__(self):
##        print("calling ifelse on", self.guard, self.ifval, self.elseval)
#        if self.guard is not None:
#            if isinstance(self.ifval,cachedifthenelse): self.ifval = self.ifval()
#            if isinstance(self.elseval,cachedifthenelse): self.elseval = self.elseval()
#            self.val = self.guard.if_else(self.ifval, self.elseval)
#            self.guard = None
#            self.ifval = None
#            self.elseval = None
#        return self.val

class ensemble:
    def __init__(self, guard, obj):
        self.vals = {id(obj): (guard,obj)}
        
    def get(self):
        if len(self.vals)==1:
            for nm in self.vals.values():
                return nm[1]
        return self
    
    def add(self, guard, obj):
        if id(obj) in self.vals:
            (g,obj) = self.vals[id(obj)]
            self.vals[id(obj)] = (g|guard,obj)
        else:
            self.vals[id(obj)] = (guard,obj)
            
    def __call__(self):
        ret = None
        for (g,obj) in self.vals.values():
            if isinstance(obj,ensemble): obj=obj()
            if ret is None:
                ret = obj
            else:
                ret = g.if_else(obj,ret)
        return ret
        
class values:
    def __init__(self):
        self.dic = {}
        
    def __getitem__(self, var):
        if not var in self.dic: raise NameError("name '" + var + "' is not always set")
        if isinstance(self.dic[var], ensemble): 
#            print("ifthenelsing", var)
#            if self.dic[var].guard is not None: print("* ifthenelse", var, self.dic[var].guard, "?", self.dic[var].ifval, ":", self.dic[var].elseval)
            self.dic[var]=self.dic[var]()
        return self.dic[var]
    
    def get(self, var):
        if isinstance(self.dic[var], ensemble): 
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
    
    def to_ensembles(self):
        guard = self["__guard"]
        ret = values()
        ret.dic = {nm: ensemble(guard,val) for (nm,val) in self.dic.items()}
        return ret
    
def apply_to_label(vals, orig):
#    print("appyling", vals, "to", orig)
    ifguard = vals["__guard"]

    if orig is None: 
        ret = vals.to_ensembles()
#        print("returning", ret)
        return ret
    
#    print("vals", vals)
#    print("orig", orig)
    
    ret = values()
    for nm in orig:
        if nm in vals:
#            print("orig", nm, orig.dic[nm])
            orig.dic[nm].add(ifguard, vals.get(nm))
#            if (vif:=vals.get(nm)) is (velse:=orig.get(nm)):
#                ret[nm] = vif
#            else:
#                if ifguard is True or ifguard is False or isinstance(ifguard,int):
#                    raise RuntimeError("trivial guard")
#                ret[nm] = cachedifthenelse(ifguard, vif, velse)

    #print("returning", ret)
    return orig  

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