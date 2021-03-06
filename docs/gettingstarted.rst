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
    
Obliv requires a recent version of Python (tested with Python 3.8 and 3.9) and uses the ``bytecode`` package (``pip install bytecode``).

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

``for`` loops
.............

It is possible to use for loops over ranges ``range(x)`` where ``x`` is an oblivious variable. Only positive integer strides are supported. 

Since ``oblif`` cannot know when the bound is reached, it is necessary to provide an upper bound. There are two approaches. One is to include a ``break`` statement in the loop, e.g.::

  for i in range(x):   # x is a data-oblivious value
    if x==5: break     # make sure loop executed at most 5 times: can be here ...
    ret = i
    if i==5: break     # ... or here (this is slightly more efficient)
	
An alternative is to use ``orange`` from ``oblif.iterators``, which enables to provide the oblivious maximum and the non-oblivious upper bound as a tuple::

  for i in orange((x,10)):   # x is a data-oblivious value; loop is run at most 5 times
    ret = i

For efficiency reasons, ``oblif`` does **not** check whether the initial value is smaller than the oblivious maximum (that would require an oblivious sign computation, which may be more efficient than an oblivious equality check), for example::

  x=PrivVal(-1)
  for i in orange((x,10)):
    # i never becomes equal to -1, so branch is fully executed
    ret = i
  # after branch, ret=9
  
``lambdas``
...........

For what it's worth, ``oblif`` works on lambda's as well, for example::

  oblambda = oblif(lambda x: 1 if x==3 else 0)
  xisthree = oblambda(x)

.. _cannot-do:

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

Oblif uses ``guard.if_else(..., ...)`` to select or ignore data-oblivious assignments. Both in MPyC and in PySNARK, for this to work, ``guard`` needs to be equal to either 0 or 1. Results for guards that have other values is undefined, for example::

  if a: # a is a data-oblivious value 5
    ret = 1
  else:
    ret = 0
  # branch on non-binary guard, value of ret is undefined

In fact, in most implementations, ret will be computed as ``elseval+guard*(ifval-elseval)`` and so in this example will be equal to 5...

Perform in-place operations on mutable objects
..............................................

As mentioned above, oblif will also execute non-taken branches. As a consequence, in-place modifications to objects will be executed regardless of whether a branch is taken or not, for example::

  lst = [1,2,3]
  if a: # a is a data-oblivious value
    print(id(lst))  # prints id, executed regardless of a
    lst[1] = 0      # this is an in-place modification, always executed
  else:
    print(id(lst))  # prints same id, executed regardless of a
    lst[1] = 4      # this is an in-place modification, always executed
  # lst[1] is always equal to 4 regardless of a
  
In this example, the if and else branches act on the same object. After the branch, ``lst = a.if_else(lst, lst)`` will be executed, but this has no effect since ``lst`` in both cases refers to the same object.

To still be able to perform operations on a mutable object, it needs to be copied before use, for example::

  lst = [1,2,3]
  if a: # a is a data-oblivious value
    lst = deepcopy(lst)
    print(id(lst))  # prints id, executed regardless of a
    lst[1] = 0      # this is an in-place modification on the copy of lst
  else:
    lst = deepcopy(lst)
    print(id(lst))  # prints different id, executed regardless of a
    lst[1] = 4      # this is an in-place modification on another copy of lst
  # lst[1] is 0 or 4 depending on a

(There is some experimental work to automatically copy mutable objects before they are executed in branches. This may be implemented in a future version of oblif.)

Obliviously modify global variables
...................................

Oblif only monitors access to local variables, not to globals. Because, as mentioned above, oblif also executes non-taken branches, this means that modifications to global variables in non-taken branches will be executed regardless of their guard, for example::

  @oblif def setb(a): # a is a data-oblivious variable
    global b
    if a==1:
      b = 3      # will be executed regardless of whether a==1
    else:
      b = 4      # will be executed regardless of whether a==1
    # end result is that b is a non-oblivious variable equal to 4
  
Of course, it is possible to set the value of a global variable to an obliviously computed value. The global variable will then become a data-oblivious value equal to the computed value, for example::

  @oblif def setb(a): # a is a data-oblivious variable
    global b
    if a==1:
      bval = 3      # will be obliviously set to 3 if a==1
    else:
      bval = 4      # will be obliviously set to 4 if a!=1
    # bval is a data-oblivious variable equal to 3 or 4
    b = bval        # set b to this data-oblivious variable

Access variables that may be undefined
......................................

Values set in a branch can only be accessed if they also have a well-defined value in all other branches. For example::

  @oblif
  def test(x):
      if x==3:
        ret = 1
      return ret   # error: ret has no value if (x==3) does not hold
    
However, the following is OK::

  @oblif
  def test(x):
      ret = 0
      if x==3:
        ret = 1
      return ret   # ret has value 0 if (x==3) does not hold
