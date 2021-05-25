from copy import deepcopy

class ensemble:
    def __init__(self, obj):
        self.vals = {None: (None,obj)}
        
    def get(self):
        if self.vals is None: return self.val
        
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
        if self.vals is not None:
            self.val = self.vals[None][1]
            for (g,obj) in self.vals.values():
                if g is None: continue
                if isinstance(obj,ensemble): obj=obj()
                self.val = g.if_else(obj,self.val)
            self.vals = None
        return self.val
                  
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
    
def apply_to_label(vals, orig):
    if orig is None: return vals
    
    ifguard = vals["__guard"]    
    
    ret = values()
    for nm in orig:
        if nm in vals:
            if (vif:=vals.get(nm)) is (velse:=orig.get(nm)):
                ret[nm] = vif
            elif isinstance(velse, ensemble):
                velse.add(ifguard, vif)
                ret[nm] = velse
            else:
                ret[nm] = ensemble(velse)
                ret.dic[nm].add(ifguard, vif)
                
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