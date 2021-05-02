from oblif import oblif
#from context import Ctx

from pysnark.runtime import PubVal

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
        
    def ifelse(self, ifval, elseval):
        if ifval is elseval: return ifval
        
        ifi = (ifval if isinstance(ifval,int) else ifval.val)
        oti = (elseval if isinstance(elseval,int) else elseval.val)
        
        print("calling ifelse => ", self, ifval, elseval, self.val*ifi + (1-self.val)*oti)
        return OblivVal(self.val*ifi + (1-self.val)*oti)
    
    def __and__(self, other):
        if isinstance(other,int):
            return self if other else 0
        else:
            return OblivVal(self.val&other.val)
        
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
    

@oblif
def test(x):

    ret = 1
    ix = 1
    
    print("before", ix)
    
    if x==5:
        x=10
        
    print("after", ix)
    
    while ix!=10:
        ret = ret*ix
        if ix==x: break
        ix = ix+1
        
    return ret

print("test(5) is", test(PubVal(5)).val())
    
#    a=x*x
#    b=3
#    if OblivVal(0): #x==2
#        print("** if")
#        c=1
#    else:
#        print("** else")
#        c=x*a
#    return c

#print("test(5) is", oblif(test)(PrivVal(5)))
#print("test(2) is", test(6))
