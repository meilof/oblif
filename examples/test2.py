from oblif.decorator import oblif
from oblif.types import OblivVal
from oblif.iterators import orange

#for i in orange(10,10):
#    print(i)

@oblif
def test(x):
    ret = 0
    if x==3:
        ret = 1
    return ret


#print("test(2) is", test(OblivVal(6)))

#test = lambda x: x*x if x==6 else 0
#test=oblif(test)

print("test(2) is", test(OblivVal(4)))
