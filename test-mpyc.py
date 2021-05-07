from mpyc.runtime import mpc
from oblif import oblif

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

    print("returning", ret)
    return ret

mpc.run(mpc.start())
type=mpc.SecInt()

type.ifelse = lambda self, ifval, elseval: ifval if ifval is elseval else mpc.if_else(self, ifval, elseval)
type.__deepcopy__ = lambda self, memo: self

print("test(5) is", mpc.run(mpc.output(test(type(5)))))

mpc.run(mpc.shutdown())
    
