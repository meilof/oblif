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
    
def apply_to_label(contexts, vals, cond, label):
#    print("applying to label", label, cond)
    if cond is False:
        return vals
    elif not label in contexts:
        if cond is True:
            contexts[label] = vals
            return None
        else:
            contexts[label] = vals.copy()
            contexts[label]["__guard"] &= cond
            vals["__guard"] &= (1-cond)
            return vals
    else:
        have_else = not cond is True
        guardif = vals["__guard"] & cond
        cif = values()
        corig = contexts[label]
        if have_else: celse = values()

#        print("doing ifthenelse", corig.dic.keys(), vals.dic.keys())
        for nm in corig:
            if nm in vals:
#                print("both:", nm)
                if (vif:=vals.get(nm)) is (velse:=corig.get(nm)):
                    cif[nm] = vif
                    if have_else: celse[nm] = vif
                else:
                    cif[nm] = cachedifthenelse(guardif, vif, velse)
                    if have_else: celse[nm] = vif

        cif["__guard"] = corig["__guard"]|guardif
        if have_else: celse["__guard"] = vals["__guard"] & (1-cond)
        contexts[label] = cif
        return celse if have_else else None

def values_new():
    return values()