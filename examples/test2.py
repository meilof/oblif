from oblif.decorator import oblif
from oblif.types import OblivVal
from oblif.iterators import orange

#for i in orange(10,10):
#    print(i)

@oblif
def test(x):
#    ret = 0
#    if x==3:
#        ret = 1
#    for i in range(min(10,10)):
#        print(i)
#        ret=i
#    print("after", ret)        

    for i in range(min(x,10)):
        print(i)
        ret=i
        for j in range(min(i,10)):
            print("  ", j)
            ret=j
    print("after", ret)
    return ret
#            if x==3:
#                ret = 1
#            else:
#                ret = 2
#            return ret        


print("test(2) is", test(OblivVal(6)))
