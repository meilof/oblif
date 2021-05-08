from mpyc.runtime import mpc
from oblif.decorator import oblif

@oblif
def test(x):
    return 1 if x==5 else 0

mpc.run(mpc.start())
type=mpc.SecInt()

#type.ifelse = lambda self, ifval, elseval: ifval if ifval is elseval else mpc.if_else(self, ifval, elseval)
#type.__deepcopy__ = lambda self, memo: self

print("test(5) is", mpc.run(mpc.output(test(type(5)))))

mpc.run(mpc.shutdown())
    
