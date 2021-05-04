from oblif import oblif
import pyz8z
#from pysnark.runtime import PubVal

class enc:
    def __init__(self, ct_or_key, val_or_none=None):
        if val_or_none is None:
            self.ct = ct_or_key
        else:
            self.ct = pyz8z.Z8Ciphertext(ct_or_key, val_or_none)
        
    def __bool__(self):
        raise TypeError("cannot do bool()")
        
    def ifelse(self, ifval, elseval):
        if ifval is elseval: return ifval
        ret = ifval + (1-self)*(elseval-ifval)
        return ret
    
    def __mul__(self, other):
        return enc(self.ct.mulc(other.ct) if isinstance(other, enc) else self.ct.muli(other%8))
    
    __rmul__ = __mul__
    
    def __add__(self, other):
        return enc(self.ct.addc(other.ct) if isinstance(other, enc) else self.ct.addi(other%8))
    
    __radd__ = __add__
    
    def __sub__(self, other):
        return enc(self.ct.subc(other.ct) if isinstance(other, enc) else self.ct.subi(other%8))
    
    def __rsub__(self, other):
        # TODO: make more efficient, want to avoid mul
        if isinstance(other, enc):
            return enc(other.ct.rsub(self.ct))
        else:
            return self.__mul__(7).__add__(other) # other+(-1)*self

    def dec(self, key):
        return self.ct.decrypt(key)
    
    def __and__(self, other):
        if isinstance(other,int):
            return self if other else 0
        else:
            return self.__mul__(other)
        
    __rand__ = __and__

@oblif
def test(x):
    if x:
        return 4
    else:
        return 5

#print("test(0) is", test(PubVal(0)))
#print("test(1) is", test(PubVal(1)))

print("loading keys...")
key = pyz8z.Z8EncryptKey()
print("done")
   
print("test(0) is", test(enc(key, 0)).dec(key))
print("test(1) is", test(enc(key, 1)).dec(key))
    
#    a=x*x
#    b=3
#    if OblivVal(0): #x==2
#        print("** if")
#        c=1
#    else:
#        print("** else")
#        c=x*a
#    return c

#print("test(5) is", oblif(test)(PrivVal(5)))
#print("test(2) is", test(6))
