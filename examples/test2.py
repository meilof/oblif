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
    ret=1
    for i in range(min(x,2)):
#        print("doing")
        k=(1 if x==4 else 2 if x==5 else 3)
        print("k is", k)
#        if k==1: ret=0
    return k


#print("test(2) is", test(OblivVal(6)))

#test = lambda x: x*x if x==6 else 0
#test=oblif(test)

print("test(2) is", test(OblivVal(4)))
