import sys
from oblif.decorator import oblif
from oblif.types import OblivVal
#from context import Ctx

#from pysnark.runtime import PubVal


    

@oblif
def test(x):
    ret = 0
    if x==3:
        ret = 1
    return ret
    
#    ret=1
#    for i in range(min(x,5)):
##        ret+=i*(ret+1)-i
##        print("ret", ret)
#        #print(i)
#        k=(1 if x==4 else 2 if x==5 else 3)
#        print(k)
#        if k==1: ret=0
#        #print(i)
#    return k
#    
#    
#    ret = 1
#    ix = 1
#    
#    print("before", ix, x)
#    
#    if x==5:
#        x=10
#        
#    print("after", ix, x)
#    
#    test_ = 3
#    
#    while ix!=10:
#        print("guard is", __guard)
#        ret = ret*ix
#        #if ret==120: return ret
#        if ix==x: break
#        ix = ix+1
#        test_ = test_ + 1
#        
#    print("test_", test_)
#
#    for i in range(1, min(x+1,10)):
#        print("cur", i)
#        ret = ret*i
#        print("ret", ret)
        
#    print("after, ret is", ret)
#        
#    print("returning", ret)
#    return ret

print("test(5) is", test(OblivVal(4)))
    
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
