from oblif.decorator import oblif
from pysnark.runtime import PubVal
from oblif.iterators import orange

@oblif
def test(x):
	ret = 0
	for i in orange((10,x)):
		ret+=1
		#if i+1==10: break
	return ret

print("test(2) is", test(PubVal(6)))
