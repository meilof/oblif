from copy import deepcopy
from inspect import getframeinfo, stack

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
            return tuple([self.guard.ifelse(x,y) for (x,y) in zip(self.ifval, self.elseval)])
        return self.guard.ifelse(self.ifval, self.elseval)
    
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
                    nwctx[nm] = cachedifthenelse(guard, vals.dic[nm], self.contexts[label].dic[nm])
            self.contexts[label] = cor_dict(nwctx)
#            print_ctx("result of merge:", nwctx)
            
    def label(self, label):
#        print_ctx("entering label", label, "with context", self.vals)
#        if label in self.contexts: 
#            print("and context", self.contexts[label])
#        else:
#            print("and no context")
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
            self.apply_to_label(self.vals, True, label)
            self.vals = None
        else:
            isobliv = True
#            print_ctx("* if, guard is oblivious", guard)
            self.apply_to_label(self.vals, 1-guard, label) # TODO: why not ~?
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
            self.apply_to_label(self.vals, True, label)
            self.vals = None
        else:
            isobliv = True
#            print_ctx("* if, guard is oblivious", guard)
            self.apply_to_label(self.vals, guard, label)
            self.vals["__guard"] &= (1-guard) # TODO: why not ~?
        
    def stack(self, stack):
#        print("stacking", stack)
        self.vals["__stack"] = stack
        
    def unstack(self):
#        print("calling unstack")
        stack = self.vals.dic["__stack"]
        if isinstance(stack, cachedifthenelse): stack=stack()
        ret = tuple(reversed(stack)) # ?!
#        print("stack is", ret)
        del self.vals.dic["__stack"] # TODO?!
        #self.vals.reads.remove("__stack")
        return ret
            
    def jmp(self, stack, label):
#        print("jmp", stack, label)
        self.vals["__stack"] = stack
        self.apply_to_label(self.vals, True, label)
        self.vals = None
#        print_ctx("jmp done")

    def ret(self, arg, label): # same as jmp
#        print("calling ret", arg, label, self.vals)
        self.vals["__stack"] = (arg,)
        self.apply_to_label(self.vals, True, label)  # TODO: sufficient to only apply __stack?!
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
                    self.ctx.apply_to_label(self.ctx.vals, True, label)
                    self.ctx.vals = None
                    return
                self.cur = self.start
                return
            
            if self.cur+self.step>=self.maxi or (isinstance(self.maxo,int) and self.cur+self.step>=self.maxo):
#                print("exceeded max")
                self.ctx.apply_to_label(self.ctx.vals, True, label)
                self.ctx.vals = None
                self.cur = None
                return
            
            if not isinstance(self.maxo,int):
#                print("obliviously updating guard", "cur", self.cur, "step", self.step, "maxo", self.maxo, "guard", self.ctx.vals["__guard"])
                
                dostop = 0
                for i in range(self.cur+1, self.cur+self.step+1):
#                    print("equals", i, self.maxo, (i==self.maxo))
                    dostop = (i==self.maxo)|dostop
                self.ctx.apply_to_label(self.ctx.vals, dostop, label)
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
        if isinstance(arg, self.ObliviousRange): arg.foriter(label)