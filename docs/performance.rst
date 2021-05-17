Performance
===========

Use of ``oblif`` incurs a performance overhead both at the Python level and at
the data-oblivious level. ``oblif`` takes various measures to minimize this 
overhead, but still, a data-oblivious implementation of an algorithm directly
in Python will typically be faster.

Python overhead
---------------

The ``oblif`` decorator works by transforming Python bytecode using branches
into equivalent code that performs the branches non-obliviously. This code
will be a constant factor (5-10x?) larger than the original code. Stores and
loads of local variables are replaced by dictionary look-ups, and for variables
that hold a data-oblivious variables, a data structure is kept for computing
the value of the variable when needed.

If no data-oblivious variables occur, then no unnecessary branches are taken,
but still, the code needed to enable data-oblivious branches is there. This
means that code using ``oblif`` will run a constant factor (5-10x?) slower than
non-oblivious code even in this case.

Data-oblivious overhead
-----------------------

Code using oblif may perform slightly more computations on data-oblivious values
than needed. For example, at each branching point, the value of the current
guard is computed even in situations where this is strictly not needed. This may
be improved in the future, but if performance is of the essence, for example
because data-oblivious computations are very expensive, it is probably better
to avoid the use of oblif.