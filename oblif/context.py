from inspect import getframeinfo, stack

from .iterators import orange, ObliviousIterator, IteratorWrapper
from .values import apply_to_label, apply_to_labels, values_new
    
def print_ctx(*args):
    myfilename =  getframeinfo(stack()[0][0]).filename
    ix = 1
    while getframeinfo(stack()[ix][0]).filename == myfilename: ix+=1
    caller = getframeinfo(stack()[ix][0])
    print("["+caller.filename+":"+str(caller.lineno)+"]", *args)
  
def trytobool(val):
    try:
        return bool(val)
    except:
        return val
    
def boolneg(val):
    if val is True: return False
    if val is False: return True
    return 1-val

class Ctx:
    def __init__(self):
        self.vals = values_new()
        self.vals["__guard"] = 1
#        vals0 = values_new()
#        vals0["__guard"] = 1
        self.contexts = {}

    def get(self, var):
#        print_ctx("calling get on", var, "with", self.vals)
        return self.vals[var]

    def set(self, val, var):
#        print_ctx("calling set var=", var, "val=", val, "with", self.vals)
        self.vals[var] = val
            
    def label(self, label, nstack):    
        if label in self.contexts and self.contexts[label] is not None:
#            print("executing code", self.contexts[label])
            self.vals = self.contexts[label]
#            print_ctx("entering", label, "under guard", self.vals["__guard"])
            del self.contexts[label]
            if nstack:
                ret = tuple([self.vals["__stack"+str(i)] for i in range(nstack-1,-1,-1)])
                for i in range(nstack): del self.vals["__stack"+str(i)]
                return ret
            else:
                return True
        else:
#            print_ctx("not entering", label)
            return False
    
    def pjif(self, stack, labelnext, labeljump):
#        print_ctx("calling pjif, label=", labelnext, "/", labeljump, "curguard", self.vals["__guard"], "jumpguard", stack[-1])
#        if labelnext in self.contexts and self.contexts[labelnext] is not None: print("prev next guard ", self.contexts[labelnext]["__guard"])
#        if labeljump in self.contexts and self.contexts[labeljump] is not None: print("prev jump guard ", self.contexts[labeljump]["__guard"])
        self.stack(stack[:-1])
        guard = trytobool(stack[-1])
#        guari = not guard if isinstance(guard,bool) else 1-guard
        [self.contexts[labelnext], self.contexts[labeljump]] = \
            apply_to_labels(self.vals, self.contexts.get(labelnext), self.contexts.get(labeljump), guard)
#         = apply_to_label(self.vals, , guari)
#        if self.contexts[labelnext] is not None: print("next guard ", self.contexts[labelnext]["__guard"])
#        if self.contexts[labeljump] is not None: print("jump guard ", self.contexts[labeljump]["__guard"])
        self.vals = None
            
    def pjit(self, stack, labelnext, labeljump):
#        print_ctx("calling pjif, stack=", stack, "label=", labelnext, "/", labeljump, "guard", stack[-1])
        self.stack(stack[:-1])
        guard = trytobool(stack[-1])
        [self.contexts[labeljump], self.contexts[labelnext]] = \
            apply_to_labels(self.vals, self.contexts.get(labeljump), self.contexts.get(labelnext), guard)
#        guari = not guard if isinstance(guard,bool) else 1-guard
#        self.contexts[labelnext] = apply_to_label(self.vals, self.contexts.get(labelnext), guari)
#        self.contexts[labeljump] = apply_to_label(self.vals, self.contexts.get(labeljump), guard)
        self.vals = None
        
    def stack(self, stack):
#        print("stacking", stack)
        for i in range(len(stack)): self.vals["__stack"+str(i)] = stack[i]
        
    def jmp(self, stack, label):
#        print("jmp", label, "curguard", self.vals["__guard"])
        self.stack(stack)
        self.contexts[label] = apply_to_label(self.vals, self.contexts.get(label))
        self.vals = None

    def ret(self, arg, label): # same as jmp
#        print("calling ret", arg, label)
        guard = self.vals.dic["__guard"]
        self.vals.clear()
        self.vals["__guard"] = guard
        self.stack((arg,))
        self.contexts[label] = apply_to_label(self.vals, self.contexts.get(label))
        self.vals = None
        
    def range(self, *args):
        def _range(*args):
            if len(args)==1:
                return orange((args[0],None))
            elif len(args)==2:
                return orange(args[0],(args[1],None))
            elif len(args)==3:
                return orange(args[0],(args[1],None),args[2])
            else:
                return range(*args)
        return _range
    
    def getiter(self, it):
        return iter(it) if isinstance(it, ObliviousIterator) else IteratorWrapper(iter(it))
        