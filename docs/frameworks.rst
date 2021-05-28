Supported data-oblivious frameworks
===================================

MPyC
----

MPyC is a framework for multi-party computation (privacy-preserving computation by distributing the computation among multiple parties based such that no party knows which values are being computed on).

Oblif works out of the box with the master branch of MPyC available at `GitHub <https://github.com/lschoe/mpyc>`_, e.g.::

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

Oblif can be used with the MPyC release on PyPi by performing the following monkey-patch::

  type=mpc.SecInt()
  type.ifelse = lambda self, ifval, elseval: ifval if ifval is elseval else mpc.if_else(self, ifval, elseval)
  type.__deepcopy__ = lambda self, memo: self
  
PySNARK
-------

PySNARK is a framework, inspired by MPyC, for programming verifiable computations (aka zk-SNARKs) in Python. Oblif works with the master branch of PySNARK available at `GitHub <https://github.com/meilof/pysnark>`_, e.g.::


    from oblif.decorator import oblif
    from pysnark.runtime import PubVal

    @oblif
    def test(x):
        ret = 0
        if x==3:
            ret = 1
        return ret

    print("test(2) is", test(PubVal(6)))
    
MP-SPDZ
-------

`MP-SPDZ <https://github.com/data61/MP-SPDZ>`_ implements a suite of multi-party computation protocols by compiling programs written in Python into an internal representation. It is possible to use `oblif` with MP-SPDZ by monkey-patching its data types to support binary operators on bits, for example::

    from oblif.decorator import oblif

    sint.__and__ = sint.bit_and
    sint.__rand__ = sint.bit_and
    sint.__or__ = sint.bit_or
    sint.__ror__ = sint.bit_or
    sint.__deepcopy__ = lambda self, memo: return self

    def test(actual, expected):
        actual = actual.reveal()
        print_ln('expected %s, got %s', expected, actual)

    a = sint(1)
    b = sint(2)

    @oblif 
    def test_is_two(x):
        return 1 if x==2 else 0

    test(test_is_two(b), 1)
    test(test_is_two(a), 0)

    @oblif
    def test_for(x):
        ret = 1
        for i in range(min(x, 10)):
            ret = i
        return ret

    test(test_for(sint(5)), 4)

PyZ8Z
-----

`PyZ8Z <https://github.com/meilof/demo_z8z>`_ is an experimental Python binding of Zama's Z/8Z demo to perform fully homomorphic encryption on 3-bit integers. An example of using this binding in comination with oblif can be found `here <https://github.com/meilof/oblif/blob/main/examples/test-tfhe.py>`_.

Other oblivious data types
--------------------------

Oblif is designed such that it can work in principle with any "oblivious" data type with the following requirements

 * The datatype should raise an exception if ``.__int__()`` or ``.__bool__()`` is called on it
 * The datatype should support a ``.if_else(ifval, elseval)`` operation, which is called on a guard and should obliviously select ifval if the guard is satisfied, and elseval if the guard is not satisfied. This may be implemented as ``elseval+guard*(ifval-elseval)``
 * The datatype shuld support boolean logic for guards, with 0 representing boolean ``False`` and 1 representing boolean ``True``: `.__and__(other)` for binary AND (where the other operand is another oblivious value/True/False/0/1), ``__or__`` for binary OR (where the other operand is another oblivious value/True/False/0/1), and ``1-self`` (i.e., ``.__rsub__(1)`` for binary negation)
 * For ``for`` loops, the datatype should support comparison ``.__ne__(int)``
 * It is recommended that the datatype is immutable. This means that it does not support in-place operators such as `__iadd__` and that it implements ``.__deepcopy__(memo)`` by returning ``self``. By not supporting in-place modification, it is ensured that changes in different branches do not affect each other. By returning ``self`` in deepcopy, it is ensured that if oblivious values occur in another data structure that is deepcopied (as advised under "getting started"), oblif can detect whether or not their value is changed, which is important for efficiency. Deepcopying may become the default in future versions of oblif so then ``__deepcopy__`` *must* return ``self``.