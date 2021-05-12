class OblivVal:
    def __init__(self, val):
        self.val = val
        
    def __repr__(self):
        return "{"+repr(self.val)+"}"
        
    def assert_bool(self):
        if self.val!=0 and self.val!=1:
            raise ValueError("not boolean")
            
    def __invert__(self):
        return OblivVal(1-self.val)
            
    def __bool__(self):
        raise TypeError("cannot bool() an OblivVal")
        
    def if_else(self, ifval, elseval):
        if ifval is elseval: return ifval
        
        ifi = (ifval.val if isinstance(ifval,OblivVal) else ifval)
        oti = (elseval.val if isinstance(elseval,OblivVal) else elseval)
        
        #print("calling ifelse => ", self, ifval, elseval, self.val*ifi + (1-self.val)*oti)
        return OblivVal(self.val*ifi + (1-self.val)*oti)
    
    def __and__(self, other):
        if isinstance(other,int):
            return self if other else 0
        else:
            return OblivVal(self.val&other.val)
        
    __rand__ = __and__
        
    def __or__(self, other):
#        print("calling __or__")
        if isinstance(other, int):
            return 1 if other else self
        else:
            return OblivVal(self.val|other.val)
        
    __ror__ = __or__
        
    def __eq__(self, other):
#        print("call to eq")
        return OblivVal(1 if self.val==(other if isinstance(other,int) else other.val) else 0)
    
    def __ne__(self, other):
#        print("call to ne")
        return OblivVal(1 if self.val!=(other if isinstance(other,int) else other.val) else 0)
    
    def __mul__(self, other):
        return OblivVal(self.val*(other if isinstance(other,int) else other.val))
    
    __rmul__ = __mul__
    
    def __add__(self, other):
        return OblivVal(self.val+(other if isinstance(other,int) else other.val))
    
    __radd__ = __add__
    
    def __sub__(self, other):
        return OblivVal(self.val-(other if isinstance(other,int) else other.val))
        
    def __rsub__(self, other):
        return OblivVal((other if isinstance(other,int) else other.val)-self.val)

    __rand__ = __and__
    
    def __deepcopy__(self, memo):
        return self
        