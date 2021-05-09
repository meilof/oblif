from copy import deepcopy

class cachedifthenelse:
    def __init__(self, guard, ifval, elseval):
        self.guard = guard
        self.ifval = ifval
        self.elseval = elseval
    
    def __call__(self):
#        print("calling ifelse on ", self.ifval, self.elseval)
        if isinstance(self.ifval,cachedifthenelse): self.ifval = self.ifval()
        if isinstance(self.elseval,cachedifthenelse): self.elseval = self.elseval()
        if isinstance(self.ifval, tuple):
            return tuple([self.guard.if_else(x,y) for (x,y) in zip(self.ifval, self.elseval)])
        return self.guard.if_else(self.ifval, self.elseval)
        
class cor_dict:
    def __init__(self, dic):
        self.dic = dic
        self.reads = set()
        
    def __getitem__(self, var):
        if not var in self.reads:
#            print("deepcopying", var)
            self.dic[var] = deepcopy(self.dic[var])
            self.reads.add(var)
            if isinstance(self.dic[var], cachedifthenelse): self.dic[var]=self.dic[var]()
        return self.dic[var]
    
    def __setitem__(self, var, val):
        self.dic[var] = val
        self.reads.add(var)
        
    def __repr__(self):
        return "{" + ", ".join([repr(nm)+": " + repr(self.dic[nm]) for nm in self.reads]) + "}"
    
def apply_to_label(contexts, vals, cond, label):
#        print_ctx("applying to label", label)
    if not label in contexts:
#            print_ctx("first time, setting dict to", vals)
        contexts[label] = cor_dict(dict(vals.dic))
        contexts[label]["__guard"] &= cond
#            if isinstance(cond, bool):
#                # do nto need to deepcopy if we have an unconditional jump
#                self.contexts[label].reads = set(vals.reads)
    else:
        guard = vals["__guard"] & cond
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