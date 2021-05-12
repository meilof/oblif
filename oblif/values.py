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
        
    def __getitem__(self, var):
        if isinstance(self.dic[var], cachedifthenelse): self.dic[var]=self.dic[var]()
        return self.dic[var]
    
    def __setitem__(self, var, val):
        self.dic[var] = val
        
    def __repr__(self):
        return repr(self.dic)
    
def apply_to_label(contexts, vals, cond, label):
#        print_ctx("applying to label", label)
    if not label in contexts:
#            print_ctx("first time, setting dict to", vals)
        if cond is True:
            contexts[label] = vals
            return None
        else:
            contexts[label] = cor_dict(dict(vals.dic))
            contexts[label]["__guard"] &= cond
            vals["__guard"] &= (1-cond)
            return vals
    else:
        if cond is True:
            guard1 = vals["__guard"]

            d1old = contexts[label].dic
            d2old = vals.dic
            d1new = {}

            for nm in d1old:
                if nm in d2old:
                    if d1old[nm] is d2old[nm]:
                        d1new[nm] = d1old[nm]
                    else:
                        d1new[nm] = cachedifthenelse(guard1, d2old[nm], d1old[nm])
            d1new["__guard"] = d1old["__guard"]|d2old["__guard"]
            contexts[label].dic = d1new            
            return None
        else:
            guard1 = vals["__guard"] & cond
            guard2 = vals["__guard"] & (1-cond)
            
            d1old = contexts[label].dic
            d2old = vals.dic
            d1new = {}
            d2new = {}

            for nm in d1old:
                if nm in d2old:
                    if d1old[nm] is d2old[nm]:
                        d1new[nm] = d1old[nm]
                        d2new[nm] = d1old[nm]
                    else:
                        d1new[nm] = cachedifthenelse(guard1, d2old[nm], d1old[nm])
                        d2new[nm] = d2old[nm]

            d1new["__guard"] = guard1
            d2new["__guard"] = guard2
            contexts[label].dic = d1new
            return cor_dict(d2new)


def values_new():
    return cor_dict({})