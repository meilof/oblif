from inspect import getframeinfo, stack

from .iterators import orange, ObliviousRange
from .values import apply_to_label, values_new
    
def print_ctx(*args):
    myfilename =  getframeinfo(stack()[0][0]).filename
    ix = 1
    while getframeinfo(stack()[ix][0]).filename == myfilename: ix+=1
    caller = getframeinfo(stack()[ix][0])
    print("["+caller.filename+":"+str(caller.lineno)+"]", *args)
  
class IterWrapper:
    def __init__(self, it):
        self.it = it
        
    def __next__(self):
        return self.it.__next__()
    
    def __deepcopy__(self, memo):
#        print("deepcopy")
        return self

class Ctx:
    def __init__(self):
        self.vals = values_new()
        self.vals["__guard"] = 1
        self.contexts = {}

    # TODO: switch to __getitem__, __setitem__
    def get(self, var):
#        print_ctx("calling get on", var, "with", self.vals)
        return self.vals[var]
#    

    def set(self, var, val):
#        print_ctx("calling set", var, val, "with", self.vals)
        self.vals[var] = val
            
    def label(self, label):
#        print_ctx("entering label", label, "with context", self.vals)
#        if label in self.contexts: 
#            print("and context", self.contexts[label])
#        else:
#            print("and no context")
        if self.vals:
            self.vals = apply_to_label(self.contexts, self.vals, True, label)
        if label in self.contexts:
            self.vals = self.contexts[label]
            del self.contexts[label]
#            print_ctx("executing code under guard", self.vals["__guard"])
            return True
        else:
#            print_ctx("no reason to execute code, skipping")
            return False
        
    def pjif(self, stack, label):
        self.vals["__stack"] = tuple(stack[:-1])
        guard = stack[-1]
#        print_ctx("calling pjif, stack=", self.vals.dic["__stack"], "guard=", guard, "label=", label)
        
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
            self.vals = apply_to_label(self.contexts, self.vals, True, label)
        else:
#            print_ctx("* if, guard is oblivious", guard)
            self.vals = apply_to_label(self.contexts, self.vals, 1-guard, label) # TODO: why not ~?
            
    def pjit(self, stack, label):
        self.vals["__stack"] = tuple(stack[:-1])
        guard = stack[-1]
#        print_ctx("calling pjit, stack=", self.vals.dic["__stack"], "guard=", guard, "label=", label)
        
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
            self.vals = apply_to_label(self.contexts, self.vals, True, label)
        else:
#            print_ctx("* if, guard is oblivious", guard)
            self.vals = apply_to_label(self.contexts, self.vals, guard, label)
        
    def stack(self, stack):
#        print("stacking", stack)
        self.vals["__stack"] = stack
        
    def unstack(self):
#        print("calling unstack", self.vals.dic["__stack"])
        stack = self.vals["__stack"]
        #if isinstance(stack, cachedifthenelse): stack=stack()
        ret = tuple(reversed(stack)) # ?!
#        print("stack is", ret)
        del self.vals.dic["__stack"] # TODO?!
        #self.vals.reads.remove("__stack")
        return ret
            
    def jmp(self, stack, label):
#        print("jmp", stack, label)
        self.vals["__stack"] = stack
        self.vals = apply_to_label(self.contexts, self.vals, True, label)
#        print_ctx("jmp done")

    def ret(self, arg, label): # same as jmp
#        print("calling ret", arg, label, self.vals)
        self.vals["__stack"] = (arg,)
        self.vals = apply_to_label(self.contexts, self.vals, True, label)  # TODO: sufficient to only apply __stack?!
        
#    def doret(self, label):
#        print("calling doret", label)
#        self.label(label)
#        return self.vals["__ret"]

    def range(self, *args):
        return orange(self, *args)
            
    def foriter(self, arg, label):
#        print("called foriter", arg)
        if isinstance(arg.it, ObliviousRange): arg.it.foriter(label)
        
    def getiter(self, itr):
        #return iter(itr)
        return IterWrapper(iter(itr))
        