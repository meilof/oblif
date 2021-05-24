from oblif.decorator import oblif
from oblif.types import OblivVal
from oblif.iterators import orange

#for i in orange(10,10):
#    print(i)

@oblif
def test(x):
    # moet 1 uitkomen, komt 3 uit
#    ret = 0
#    if x==3:
#        ret = 1
#    print("now after")
#    return ret
    ret=0
    #for i in range(2):
    if x==1: ret=1
        
    # guard is back to one
        
    if x==2: ret=2
    return ret

#            ctr = 0
#            for i in range(min(x,10)):
#                ctr += 1
#            return ctr


#print("test(2) is", test(OblivVal(6)))

#test = lambda x: x*x if x==6 else 0
#test=oblif(test)

print("test(2) is", test(OblivVal(5)))
