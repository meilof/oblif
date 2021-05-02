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
        
    return ret

mpc.run(mpc.start())
type=mpc.SecInt()

print("test(5) is", mpc.run(mpc.output(test(type(5)))))

mpc.run(mpc.shutdown())
    
