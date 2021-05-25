import logging
import unittest

from oblif.iterators import orange
from oblif.decorator import oblif
from oblif.types import OblivVal

def _val(x):
    return x.val if isinstance(x, OblivVal) else x

def call_counter(func):
    def helper(*args, **kwargs):
        helper.calls += 1
        return func(*args, **kwargs)
    helper.calls = 0
    return helper

class TestOblif(unittest.TestCase):   
    
    def test_asetup(self):
        OblivVal.if_else = call_counter(OblivVal.if_else)
    
    def dotest(self, fn, *args):
        o1 = fn(*args)
        o2 = _val(oblif(fn)(*(map(OblivVal, args))))
        o3 = _val(oblif(fn)(*args))
        self.assertEqual(o1, o2)
        self.assertEqual(o1, o3)
        
    def test_fn_return_none(self):
        def fn_return_none():
            pass
        self.dotest(fn_return_none)
    
    def test_fn_return(self):
        def fn_return():
            return 1        
        self.dotest(fn_return)
        self.dotest(fn_return)
        
    def test_fn_compute_equal(self):
        def fn_compute_equal(x, y):
            return 1 if x==y else 0
        self.dotest(fn_compute_equal, 3, 4)
        self.dotest(fn_compute_equal, 3, 3)
        
    def test_fn_if(self):
        def fn_if(x):
            ret = 0
            if x==3:
                ret = 1
            return ret
        self.dotest(fn_if, 3)
        self.dotest(fn_if, 4)
        
    def test_fn_ifelse(self):
        def fn_ifelse(x):
            if x==3:
                ret = 1
            else:
                ret = 2
            return ret        
        self.dotest(fn_ifelse, 1)
        self.dotest(fn_ifelse, 3)
        
    def test_fn_for(self):
        def fn_for(x):
            ctr = 0
            for i in range(min(x,10)):
                ctr += 1
            return ctr
        self.dotest(fn_for, 1)
        self.dotest(fn_for, 2)
        self.dotest(fn_for, 9)
        self.dotest(fn_for, 10)
        self.dotest(fn_for, 11)
        
        
    def test_fn_for_ternary(self):
        def fn_for_ternary(x):
            ret=1
            for i in range(min(x,5)):
                k=(1 if x==4 else 2 if x==5 else 3)
                if k==1: ret=0
            return k
        self.dotest(fn_for_ternary, 2)
        self.dotest(fn_for_ternary, 3)
        self.dotest(fn_for_ternary, 4)
        self.dotest(fn_for_ternary, 5)

    def test_fn_while(self):
        def fn_while(x):
            ret = 1
            ix = 1

            if x==5:
                x=10

            while ix!=10:
                ret = ret*ix
                if ret==120: return ret
                if ix==x: break
                ix = ix+1
                
            return ret
        self.dotest(fn_while, 1)
        self.dotest(fn_while, 2)
        self.dotest(fn_while, 3)
        self.dotest(fn_while, 4)
        self.dotest(fn_while, 5)
        self.dotest(fn_while, 6)

    def test_fn_for2(self):
        def fn_for2(x):
            ret=1
            for i in range(1, min(x+1,10)):
                ret = ret*i
            return ret
        self.dotest(fn_for2, 1)
        self.dotest(fn_for2, 2)
        self.dotest(fn_for2, 8)
        self.dotest(fn_for2, 9)
        self.dotest(fn_for2, 10)
        self.dotest(fn_for2, 111)

    def test_fn_if2(self):
        def fn_if2(x):
            a=x*x
            b=3
            if x==2:
                c=1
            else:
                c=x*a
            return c        
        self.dotest(fn_if2, 1)
        self.dotest(fn_if2, 2)
        
    def test_recursive_for(self):
        def fn(x):
            for i in range(min(x,10)):
                ret=i
                for j in range(min(i,10)):
                    ret=j
            return ret
        self.dotest(fn, 1)
        self.dotest(fn, 2)
        self.dotest(fn, 8)
        self.dotest(fn, 9)
        self.dotest(fn, 10)
        self.dotest(fn, 111)
            
    def test_recursive_for_orange(self):
        def fn(x):
            for i in orange(x,10):
                ret=i
                for j in orange(i,10):
                    ret=j
            return ret
        self.dotest(fn, 1)
        self.dotest(fn, 2)
        self.dotest(fn, 8)
        self.dotest(fn, 9)
        self.dotest(fn, 10)
        self.dotest(fn, 111)
        
    def test_break_in_for(self):
        def fn(x):
            ret=0
            for i in range(min(x,10)):
                if i==x-1: break
                ret=i
                for j in range(min(i,10)):
                    ret=j
            return ret
        self.dotest(fn, 1)
        self.dotest(fn, 2)
        self.dotest(fn, 8)
        self.dotest(fn, 9)
        self.dotest(fn, 10)
        self.dotest(fn, 111)
        
    def test_for_no_ops(self):
        def fn(x):
            for i in range(min(x,10)):
                if i==x-1: break
        self.dotest(fn, 1)
        self.dotest(fn, 2)
        self.dotest(fn, 8)
        self.dotest(fn, 9)
        self.dotest(fn, 10)
        self.dotest(fn, 111)
        
    def test_z_print(self):
        logging.basicConfig()
        #log = logging.getLogger("LOG")
        #
        print()
        print("calls to if_else:", OblivVal.if_else.calls)


            
if __name__ == '__main__':
    unittest.main()
    
    