from pysnark.runtime import PubVal
from oblif.decorator import oblif

@oblif
def test(x):
  if x<3:
    ret = 0
  elif 3<=x<5:
    ret = 1
  else:
    ret = 2
  return ret

for i in range(8): print("test("+str(i)+") is", test(PubVal(i)).val())
