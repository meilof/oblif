from inspect import getframeinfo, stack

def ifelse(guard, ifv, elsev):
    print("calling ifelse", guard, guard.share, "?",
                            ifv, ifv.share if not isinstance(ifv, int) else None, ":",
                            elsev, elsev.share if not isinstance(elsev, int) else None)
    try:
        return guard.ifelse(ifv, elsev)
    except AttributeError:
        print("attribute error")
        return elsev + guard*(ifv-elsev)

class cor_dict:
    def __init__(self, dic):
        self.dic = dic
        self.reads = set()
        
    def __getitem__(self, var):
        if not var in self.reads:
            # todo: deep copy
            self.reads.add(var)
        return self.dic[var]
    
    def __setitem__(self, var, val):
        self.dic[var] = val
        self.reads.add(var)
        
    def __repr__(self):
        return "{" + ", ".join([repr(nm)+": " + repr(self.dic[nm]) for nm in self.reads]) + "}"
    
def print_ctx(*args):
    myfilename =  getframeinfo(stack()[0][0]).filename
    ix = 1
    while getframeinfo(stack()[ix][0]).filename == myfilename: ix+=1
    caller = getframeinfo(stack()[ix][0])
    print("["+caller.filename+":"+str(caller.lineno)+"]", *args)
    
class Ctx:
    def __init__(self):
        self.vals = cor_dict({"__guard": 1})
        self.contexts = {}
        
        
#        self.cond = []
#        self.vals = [{}]
#        
#        self.contexts = {} # (pair of cond, vals)
#    

    # TODO: switch to __getitem__, __setitem__
    def get(self, var):
#        print_ctx("calling get on", var, "with", self.vals)
        return self.vals[var]
#        def _get():
#            for d in reversed(self.vals):
#                if var in d: return d[var]
#            raise ValueError("Attempt to access unset variable: " + str(var))
#        ret = _get()
#        self.vals[-1][var] = ret # TODO: deepcopy
#        return ret
#    

    def set(self, var, val):
#        print_ctx("calling set", var, val, "with", self.vals)
        self.vals[var] = val

    def apply_to_label(self, vals, cond, label):
#        print_ctx("applying to label", label)
        if not label in self.contexts:
#            print_ctx("first time, setting dict to", vals)
            self.contexts[label] = cor_dict(dict(vals.dic))
            self.contexts[label]["__guard"] &= cond
        else:
            guard = vals["__guard"] & cond
#            print_ctx("oblivious merge")
#            print_ctx("orig: ", self.contexts[label])
#            print_ctx("new: ", cond, guard, vals)
            # merge the two contexts
            # if we are here, we are guaranteed that cond must be oblivious,
            # otherwise we could not arrive at the label in two different ways
            nwctx = dict()
            for nm in self.contexts[label].dic:
                if nm in vals.dic:
                    nwctx[nm] = guard.ifelse(vals.dic[nm], self.contexts[label].dic[nm])
            self.contexts[label] = cor_dict(nwctx)
#            print_ctx("result of merge:", nwctx)
            
    def label(self, label):
#        print_ctx("entering label", label, "with context", self.vals)
        if self.vals:
            self.apply_to_label(self.vals, True, label)
        if label in self.contexts:
            self.vals = self.contexts[label]
            del self.contexts[label]
#            print_ctx("executing code under guard", self.vals["__guard"])
            return True
        else:
#            print_ctx("no reason to execute code, skipping")
            return False
        
    def pjif(self, guard, label):
#        print_ctx("calling pjif, guard=", guard, "label=", label)
        
        try:
            guard = bool(guard)
        except:
            pass
        
        if guard is True:
#            print_ctx("* if, guard is true, so do")
            # guard evaluates to true, so we do not want to jump
            pass
        elif guard is False:
#            print_ctx("* if, guard is false, so skip")
            # guard evaluates to false, we want to jump
            self.apply_to_label(self.vals, True, label)
            self.vals = None
        else:
            isobliv = True
#            print_ctx("* if, guard is oblivious", guard)
            self.apply_to_label(self.vals, 1-guard, label) # TODO: why not ~?
            self.vals["__guard"] &= guard
            
    def pjit(self, guard, label):
#        print_ctx("calling pjit, guard=", guard, "label=", label)
        
        try:
            guard = bool(guard)
        except:
            pass
        
        if guard is False:
#            print_ctx("* ifneg, guard is false, so do")
            # guard evaluates to false, so we do not want to jump
            pass
        elif guard is True:
#            print_ctx("* ifneg, guard is true, so skip")
            # guard evaluates to true, we want to jump
            self.apply_to_label(self.vals, True, label)
            self.vals = None
        else:
            isobliv = True
#            print_ctx("* if, guard is oblivious", guard)
            self.apply_to_label(self.vals, guard, label)
            self.vals["__guard"] &= (1-guard) # TODO: why not ~?
            
    def jmp(self, label):
#        print_ctx("calling jmp", label)
        self.apply_to_label(self.vals, True, label)
        self.vals = None
#        print_ctx("jmp done")
        
