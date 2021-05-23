from copy import deepcopy

class cachedifthenelse:
    def __init__(self, guard, ift, elset, val):
        # TODO: should we have a flag whether the value is set or not? currently we cannot cache a None...
        self.guard = guard      # guard at current branch point (if is None, then self.value assumed to be the correct value)
        self.ift = ift          # tree for "true" case (either ift or else needs to be not None if not hasval)
        self.elset = elset      # tree for "false" case
        self.val = val          # value that is cached/computed before, or None if no value
    
    def __repr__(self):
        return "[" + repr(self.val) + " " + repr(self.guard) + " ? " + repr(self.ift) + " : " + repr(self.elset) + "]"
        
    def __call__(self):
        if self.guard is None or self.val is not None: return self.val
    
        if self.ift and not self.elset: return self.ift()
        if not self.ift: return self.elset()
        
        self.val = self.guard.if_else(self.ift(), self.elset())
#        print("calling if_else", self.guard, self.ift(), self.elset(), self.val)
        return self.val
    
    def add_cond(self, guard, is_if):
        if self.guard is guard:
            pass
        elif self.guard is not None:
            if self.ift is not None: self.ift.add_cond(guard, is_if)
            if self.elset is not None: self.elset.add_cond(guard, is_if)
        elif is_if:
            self.guard = guard
            self.ift = cachedifthenelse(None, None, None, self.val)
        else:
            self.guard = guard
            self.elset = cachedifthenelse(None, None, None, self.val)
            
    def apply_to_val(self, val):
        if self.guard is None:
            return cachedifthenelse(None, None, None, val)
        else:
            return cachedifthenelse(self.guard, 
                                    self.ift.apply_to_val(val) if self.ift is not None else None, 
                                    self.elset.apply_to_val(val) if self.elset is not None else None,
                                    val)
        
    def sureval(self):
        if self.guard is None: return self.val
        if not self.ift or not self.elset: return None
        return val1 if (val1:=self.ift.sureval()) is self.elset.sureval() else None
        
def ifthenelse_merge(vif, velse):
    if vif is None and velse is None:
        return (None,None)
    elif vif is not None and velse is None:
        return (vif, vif.sureval())
    elif velse is not None and vif is None:
        return (velse, velse.sureval())
    elif vif.guard is None or velse.guard is None:
        return (vif, vif.val) # if this happens, else must already have been merged in due to caching
        #raise RuntimeError("same condition reached in two guards")
    elif vif.guard is not velse.guard:
        raise RuntimeError("inconsistent tree conditions")
        
    (lmerge,lsval) = ifthenelse_merge(vif.ift, velse.ift)
    (rmerge,rsval) = ifthenelse_merge(vif.elset, velse.elset)
    
    if lmerge is None and rmerge is None:
        vif.val = None
    elif lmerge is None:
        vif.val = rmerge.val
    elif rmerge is None:
        vif.val = lmerge.val
    else:
        vif.val = lmerge.val if lmerge.val is rmerge.val else None

    if (lsval is not None) and (lsval is rsval):
        vif.guard = None
        vif.ift = None
        vif.elset = None
    else:
        vif.ift = lmerge
        vif.elset = rmerge
        
    return (vif, lsval if lsval is rsval else None)
    
    
    # return [tree, sureval]
    # once done, switch to iterator-based design, then we can also do iterating of val based on guard instead of using apply_to_val
    # make sure that we preserve duplicates in the trees
        
class values:
    def __init__(self):
        self.dic = {}
        
    def __getitem__(self, var):
        if not var in self.dic: raise NameError("name '" + var + "' is not always set")
        if isinstance(self.dic[var], cachedifthenelse): 
#            print("getitem", var)
            self.dic[var]=self.dic[var]()
        return self.dic[var]     
    
    def __setitem__(self, var, val):
#        if val is None: raise RuntimeError("cannot set to None")
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

#    if "__stack0" in vals and "__stack1" in vals and "k" in vals:
#        print("doing apply to label")
#        print("vals", vals.dic["k"])
#        print("orig", orig.dic["k"])
#        print("")

    ifguard = vals.dic["__guard"]
    elseguard = orig.dic["__guard"]
#    print("ifguard", ifguard)
#    print("elseguard", elseguard)
    ret = values()
    for nm in orig:
        if nm in vals:
            if nm=="__guard": continue
#            print("merging", nm, vals.dic[nm], orig.dic[nm])
#            if nm=="__stack1": print("__stack1 orig", vals.dic[nm], "ifg", ifguard)
            if not isinstance(vif:=vals.dic[nm], cachedifthenelse): vif = ifguard.apply_to_val(vif)
            if not isinstance(velse:=orig.dic[nm], cachedifthenelse): velse = elseguard.apply_to_val(velse)
#            print("if", ifguard, vif)
#            print("else", elseguard, velse)
#            if nm=="__stack1": print("vif", vif, "velse", velse)
            ret[nm] = ifthenelse_merge(vif, velse)[0]
#            if nm=="__stack1":
#                print("__stack1", vif, "/", velse, "/", ret.dic[nm])

    # do this one last since we need its original value for apply_to_val
#    print("merging guards", vals.dic["__guard"], orig.dic["__guard"])
    ret["__guard"] = ifthenelse_merge(vals.dic["__guard"], orig.dic["__guard"])[0]
#    print("result", ret.dic["__guard"])
    return ret  

def apply_to_labels(vals, orig1, orig2, cond):
    if cond is True:
        return [apply_to_label(vals, orig1), orig2]
    elif cond is False:
        return [orig1, apply_to_label(vals, orig2)]
        
    guard1 = vals.dic["__guard"]    
    guard2 = deepcopy(guard1)
    guard1.add_cond(cond, True)
    guard2.add_cond(cond, False)
    
    vals["__guard"] = guard1
    ret1 = apply_to_label(vals, orig1)
    
    if orig1 is None and orig2 is None: vals = vals.copy()
        
    vals["__guard"] = guard2
    ret2 = apply_to_label(vals, orig2)
    
    ret1["__guard"] = guard1  # because may be overwritten to guard2 if we do not copy vals
    
    return [ret1,ret2]

def values_new():
    ret = values()
    ret["__guard"] = cachedifthenelse(None, None, None, 1)
    return ret