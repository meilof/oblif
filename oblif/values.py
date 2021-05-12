from copy import deepcopy

class cachedifthenelse:
    def __init__(self, guard, ifval, elseval):
        self.guard = guard
        self.ifval = ifval
        self.elseval = elseval
        self.val = None
    
    def __call__(self):
#        print("calling ifelse on", self.guard, self.ifval, self.elseval)
        if self.guard is not None:
            if isinstance(self.ifval,cachedifthenelse): self.ifval = self.ifval()
            if isinstance(self.elseval,cachedifthenelse): self.elseval = self.elseval()
            if isinstance(self.ifval, tuple):
                self.val = tuple([self.guard.if_else(x,y) for (x,y) in zip(self.ifval, self.elseval)])
            else:
                self.val = self.guard.if_else(self.ifval, self.elseval)
            self.guard = None
            self.ifval = None
            self.elseval = None
        return self.val
        
class values:
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
        if cond is True:
            contexts[label] = vals
            return None
        else:
            contexts[label] = values(dict(vals.dic))
            contexts[label]["__guard"] &= cond
            vals["__guard"] &= (1-cond)
            return vals
    else:
        have_else = not cond is True
        guardif = vals["__guard"] & cond
        dictif = {}
        if have_else: 
            guardelse = vals["__guard"] & (1-cond)
            dictelse = {}

        dictorig = contexts[label].dic
        dictiforig = vals.dic

        for nm in dictorig:
            if nm in dictiforig:
                if (vif:=dictiforig[nm]) is (velse:=dictorig[nm]):
                    dictif[nm] = vif
                    if have_else: dictelse[nm] = vif
                else:
                    dictif[nm] = cachedifthenelse(guardif, vif, velse)
                    if have_else: dictelse[nm] = vif

        dictif["__guard"] = dictorig["__guard"]|guardif
        if have_else: dictelse["__guard"] = guardelse
        contexts[label].dic = dictif
        return values(dictelse) if have_else else None

def values_new():
    return values({})