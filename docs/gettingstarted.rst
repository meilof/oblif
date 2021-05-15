Getting started with oblif
==========================

Oblif lets you write data-oblivious programs using non-data-oblivious constructs such as ``if`` and ``while``.

Privacy-preserving cryptographic frameworks such as 
`MPyC <https://github.com/lschoe/mpyc>`_ for multi-party computation and `PySNARK <https://github.com/meilof/pysnark>`_ for zk-SNARKs allow to write Python code that gets executed in a privacy-preserving way. For this, they make use of oblivious data types, e.g., ``mpc.SecInt`` for mpyc and ``PubVal`` for PySNARK. 
However, such frameworks do not allow to branch on such oblivious data types, e.g. to do ``x = a if mpc.SecInt(...) else b``.
This is necessary since the code itself is also not allowed to know whether a branch is taken or not.
Such code that does not branch on oblivious data is called data-oblivious code.

Oblif makes it possible to write programs for such cryptographic frameworks that *does* branch over oblivious data types. Oblif provides a Python decorator, ``oblif.decorator.oblif``, that re-writes such code such that it results in a data-oblivious program that performs the same computation (with some caveats, see below).
For example, effectively, the following program::

  if x==0:
    ret = 1
  else
    ret = 0

gets translated into::

  ret_if = 1
  ret_else = 0
  ret = (x==0).if_else(ret_if, ret_else)
  
Here, ``if_else`` is a function of oblivious data types that is provided e.g. by MPyC and PySNARK and that selects the first or the second argument based on whether the oblivious data is 1 or 0. (It does so by computing, in this case, ``ret_else + (ret_if-ret_else)*(x==0)``.)

Oblif supports not only ``if`` statements, but also ``for`` and ``while`` loops and oblivious return statements. For example, the following is a full example of a MPyC program using oblif::

    from mpyc.runtime import mpc
    from oblif.decorator import oblif

    @oblif
    def fac(x):
        ret=1
        for i in range(2,min(x+1, 10)):
            ret *= i
        return ret

    mpc.run(mpc.start())
    type=mpc.SecInt()
    print("test(5) is", mpc.run(mpc.output(fac(type(5)))))
    mpc.run(mpc.shutdown())

Things you can do
-----------------

``if`` statements
.................

It is possible to use ``if`` statements, including the ternary operator (``a if x else b``).

``while`` loops
...............

It is possible to use while loops. However, since Oblif does not know the values of data-oblivious value, the loop at some point needs to break based on a non-oblivious value. So the follwing code::

  # i is a data-oblivious value
  while i<10:
    i+=1
    
will run forever, since Oblif cannot figure out when to stop. However, the following is OK::

  # i is a data-oblivious value
  j = 0
  while i<10:
    i+=1
    j+=1
    if j==100: break

In this case, the loop will be executed one hundred times, but changes occuring after ``i<10`` was no longer the case, will be ignored.

Things you cannot do
--------------------

Skip code
.........

It is important to realize that, if a branch is skipped based on oblivious data, **the code is still executed**! So for example::

  if a: # a is a data-oblivious value
    print("a is true")
    ret = 1
  else:
    print("a is false")
    ret = 0
  # after this, ret is a data-oblivious value that is either 0 or 1
    
At the end of this code, ret will be a data-oblivious value that is equal to 0 or 1, as expected. However, both ``a is true`` and ``a is false`` will be printed! Because data-oblivious code cannot know whether or not the branch is taken, both branches are executed. Oblif just ensures that values from taken branches are preserved and values from non-taken branches are ignored.

Branch on non-binary oblivious data
...................................

Oblif uses ``guard.if_else(..., ...)`` to select or ignore data-oblivious assignments. Both in MPyC and in PySNARK, for this to work, ``guard`` needs to be equal to either 0 or 1.

Perform oblivious operations on mutable objects
...............................................

