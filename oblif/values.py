from copy import deepcopy

refcounts = {}

class shared_ptr(obj):
    def __init__(self, obj):
        global refcounts
        self.obj = obj
        idi=id(obj)
        if not idi in refcounts: refcounts[idi]=0
        refcounts[idi]+=1
        
    def __call__(self):
        return self.obj
    
    def __del__(self):
        global refcounts
        idi=id(obj)
        refcounts[idi] -= 1
        if refcounts[idi] == 0: del refcounts[idi]
            
    def own(self):
        if refcounts[idi]==1:
            return self
        else:
            return shared_ptr(deepcopy(self.obj))
        
        
class cachedifthenelse:
    def __init__(self, guard_ptr, ifval_ptr, elseval_ptr):
        self.guard_ptr = guard_ptr
        self.ifval_ptr = ifval_ptr
        self.elseval_ptr = elseval_ptr
        self.val_ptr = None
        
    def __call__(self):
        if self.val_ptr is None:
            guard = self.guard_ptr()
            ifval = self.ifval_ptr()
            elseval = self.elseval_ptr()
            if isinstance(ifval, tuple):
                val = tuple([guard.if_else(x,y) for (x,y) in zip(ifval, elseval)])
            else:
                val = guard.if_else(ifval, elseval)
            del self.guard_ptr
            del self.ifval_ptr
            del self.elseval_ptr
            self.val_ptr = shared_ptr(val)
        return self.val_ptr()
    
    def own(self):
        return self().own()

        
class cor_dict:
    def __init__(self, dic):
        self.dic = dic     # either shared_ptr or cacheifthenelse
        self.owns = set()
        
    def __getitem__(self, var):
        if not var in self.owns:
            self.dic[var] = self.dic[var].own()
            self.owns.add(var)
        return self.dic[var]()
    
    def __setitem__(self, var, val):
        self.dic[var] = shared_ptr(val)
        self.owns.add(var)
        
    def __repr__(self):
        return "{" + ", ".join([repr(nm)+": " + repr(self.dic[nm]) for nm in self.owns]) + "}"

def apply_to_label(contexts, vals, cond, label):
#        print_ctx("applying to label", label)
    if (not label in contexts):
        if cond is True:
            contexts[label] = vals
            return None
        else:
            # split up current context into two context, neither of which own the variables
            contexts[label] = cor_dict(dict(vals.dic))
            contexts[label]["__guard"] &= cond
            vals.owns = set()
            vals["__guard"] &= (1-guard)
            return vals
    else:
        if cond is True:
            
            
            return None
        else:
            
            
            return vals
            
        guard = vals["__guard"] & cond
        
        for nm in contexts[label].dic:
            if nm in vals.dic:
                if (cv:=contexts[label].dic[nm]) is (vv:=vals.dic[nm]):
                    
                else:
                    contexts[label][nm] = cachedifthenelse(guard, cv, vv)
        
        
#            print_ctx("oblivious merge")
#            print_ctx("orig: ", self.contexts[label])
#            print_ctx("new: ", cond, guard, vals)
        # merge the two contexts
        # if we are here, we are guaranteed that cond must be oblivious,
        # otherwise we could not arrive at the label in two different ways
        nwcor = cor_dict({})
        #nwctx = dict()
        for nm in contexts[label].dic:
            if nm in vals.dic:
                nwcor.dic[nm] = cachedifthenelse(guard, vals.dic[nm], contexts[label].dic[nm])
        contexts[label] = nwcor #cor_dict(nwctx)
#            print_ctx("result of merge:", nwctx)

def values_new():
    return cor_dict({})