from mpyc.runtime import mpc
from oblif.decorator import oblif
from oblif.iterators import orange

@oblif
def fac(x):
    ret=1
    for i in orange(2,(x+1, 10)):
        ret *= i
    return ret

mpc.run(mpc.start())
type=mpc.SecInt()
print("test(5) is", mpc.run(mpc.output(fac(type(5)))))
mpc.run(mpc.shutdown())
    
