import unittest

from oblif.types import OblivVal
from oblif.decorator import oblif

def _val(x):
    return x.val if isinstance(x, OblivVal) else x

def fn_return():
    return 1

def fn_compute_equal(x, y):
    return 1 if x==y else 0

def fn_if(x):
    ret = 0
    if x==3:
        ret = 1
    return ret

def fn_ifelse(x):
    if x==3:
        ret = 1
    else:
        ret = 2
    return ret

def fn_for(x):
    ctr = 0
    for i in range(min(x,10)):
        ctr += 1
    return ctr

class TestOblif(unittest.TestCase):   
    
    def dotest(self, fn, *args):
        self.assertEqual(fn(*args),
                         _val(oblif(fn)(*(map(OblivVal, args)))))
        
    def test_fn_return(self):
        self.dotest(fn_return)
        self.dotest(fn_return)
        
    def test_fn_compute_equal(self):
        self.dotest(fn_compute_equal, 3, 4)
        self.dotest(fn_compute_equal, 3, 3)
        
    def test_fn_if(self):
        self.dotest(fn_if, 3)
        self.dotest(fn_if, 4)
        
    def test_fn_ifelse(self):
        self.dotest(fn_ifelse, 1)
        self.dotest(fn_ifelse, 3)
        
    def test_fn_for(self):
        self.dotest(fn_for, 1)
        self.dotest(fn_for, 2)
        self.dotest(fn_for, 9)
        self.dotest(fn_for, 10)
        self.dotest(fn_for, 11)
        
        
        
        #self.assertEqual(compute_equal(3,4),
        #                 _val(oblif(compute_equal)(OblivVal(3),4)))
    

if __name__ == '__main__':
    unittest.main()
    
    