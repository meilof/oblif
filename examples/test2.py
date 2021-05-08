from oblif.decorator import oblif
from oblif.types import OblivVal

@oblif
def test(x):
    ret = 0
    if x==3:
        ret = 1
    return ret

print("test(2) is", test(OblivVal(6)))
