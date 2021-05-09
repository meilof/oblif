from .values import apply_to_label, values_new

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
            
def orange(ctx, *args):
    if len(args)==2:
        return ObliviousRange(ctx, 0, args[0], args[1], 1)
    elif len(args)==3:
        return ObliviousRange(ctx, args[0], args[1], args[2], 1)
    elif len(args)==4:
        return ObliviousRange(ctx, args[0], args[1], args[2], 3)
    else:
        raise RuntimeError("wrong number of arguments to range()")
    