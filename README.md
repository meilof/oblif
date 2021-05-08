# oblif

Oblif is a library that lets you write data-oblivious code in a non-data-oblivious way. For example:

```python
from mpyc.runtime import mpc

def test(x):
    return 1 if x==5 else 0

mpc.run(mpc.start())
print("test(5) is", mpc.run(mpc.output(test(type(5)))))
mpc.run(mpc.shutdown())
```

```
2021-05-08 13:56:22,858 Start MPyC runtime v0.7.4
Traceback (most recent call last):
    File "test-mpyc.py", line 14, in <module>
    print("test(5) is", mpc.run(mpc.output(test(type(5)))))
  File "test-mpyc.py", line 6, in test
    return 1 if x==5 else 0
  File "/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/mpyc-0.7.4-py3.8.egg/mpyc/sectypes.py", line 50, in __bool__
TypeError: cannot use secure type in Boolean expressions
```

But

```python
from mpyc.runtime import mpc
from oblif.decorator import oblif

@oblif
def test(x):
    return 1 if x==5 else 0

mpc.run(mpc.start())
type=mpc.SecInt()
type.ifelse = lambda self, ifval, elseval: ifval if ifval is elseval else mpc.if_else(self, ifval, elseval)
type.__deepcopy__ = lambda self, memo: self

print("test(5) is", mpc.run(mpc.output(test(type(5)))))

mpc.run(mpc.shutdown())
```

gives

```
2021-05-08 13:58:47,387 Start MPyC runtime v0.7.4
test(5) is 1
2021-05-08 13:58:47,394 Stop MPyC runtime -- elapsed time: 0:00:00.006167
```
