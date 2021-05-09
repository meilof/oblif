from inspect import getframeinfo, stack

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
            
    def label(self, label):
#        print_ctx("entering label", label, "with context", self.vals)
#        if label in self.contexts: 
#            print("and context", self.contexts[label])
#        else:
#            print("and no context")
        if self.vals:
            apply_to_label(self.contexts, self.vals, True, label)
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
            apply_to_label(self.contexts, self.vals, True, label)
            self.vals = None
        else:
            isobliv = True
#            print_ctx("* if, guard is oblivious", guard)
            apply_to_label(self.contexts, self.vals, 1-guard, label) # TODO: why not ~?
            self.vals["__guard"] &= guard
            
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
            apply_to_label(self.contexts, self.vals, True, label)
            self.vals = None
        else:
            isobliv = True
#            print_ctx("* if, guard is oblivious", guard)
            apply_to_label(self.contexts, self.vals, guard, label)
            self.vals["__guard"] &= (1-guard) # TODO: why not ~?
        
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
        apply_to_label(self.contexts, self.vals, True, label)
        self.vals = None
#        print_ctx("jmp done")

    def ret(self, arg, label): # same as jmp
#        print("calling ret", arg, label, self.vals)
        self.vals["__stack"] = (arg,)
        apply_to_label(self.contexts, self.vals, True, label)  # TODO: sufficient to only apply __stack?!
        self.vals = None
        
#    def doret(self, label):
#        print("calling doret", label)
#        self.label(label)
#        return self.vals["__ret"]

    class ObliviousRange:
        def __init__(self, ctx, start, max1, max2, step):
            self.ctx = ctx
            self.start = int(start)
            self.step = int(step)
            try:
                self.maxi = int(max1)
                try:
                    self.maxo = int(max2)
                except:
                    self.maxo = max2
            except:
                try:
                    self.maxi = int(max2)
                    self.maxo = max1
                except:
                    raise RuntimeError("at least one of the loop bounds must support int()")
            self.cur = None
            
        def __iter__(self):
            return self
        
        def foriter(self, label):
#            print("next", self, self.cur)
            if self.cur is None:
                if (self.start>=self.maxi) or isinstance(self.maxo,int) and self.start>=self.maxo:
#                    print("exceeded max")
                    apply_to_label(self.ctx.contexts, self.ctx.vals, True, label)
                    self.ctx.vals = None
                    return
                self.cur = self.start
                return
            
            if self.cur+self.step>=self.maxi or (isinstance(self.maxo,int) and self.cur+self.step>=self.maxo):
#                print("exceeded max")
                apply_to_label(self.ctx.contexts, self.ctx.vals, True, label)
                self.ctx.vals = None
                self.cur = None
                return
            
            if not isinstance(self.maxo,int):
#                print("obliviously updating guard", "cur", self.cur, "step", self.step, "maxo", self.maxo, "guard", self.ctx.vals["__guard"])
                
                dostop = 0
                for i in range(self.cur+1, self.cur+self.step+1):
#                    print("equals", i, self.maxo, (i==self.maxo))
                    dostop = (i==self.maxo)|dostop
                apply_to_label(self.ctx.contexts, self.ctx.vals, dostop, label)
                self.ctx.vals["__guard"] &= (1-dostop)
            
            self.cur += self.step
        
        def __next__(self):
#            print("calling next", self, self.cur)
            if self.cur is None: raise StopIteration
            return self.cur
        
    def range(self, *args):
        if len(args)==2:
            return self.ObliviousRange(self, 0, args[0], args[1], 1)
        elif len(args)==3:
            return self.ObliviousRange(self, args[0], args[1], args[2], 1)
        elif len(args)==4:
            return self.ObliviousRange(self, args[0], args[1], args[2], 3)
        else:
            raise RuntimeError("wrong number of arguments to range()")
            
    def foriter(self, arg, label):
#        print("called foriter", arg)
        if isinstance(arg.it, self.ObliviousRange): arg.it.foriter(label)
        
    def getiter(self, itr):
        #return iter(itr)
        return IterWrapper(iter(itr))
        