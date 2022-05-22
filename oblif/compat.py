def patch_mpspdz_type(tp):
    """ Monkey-patch MP-SPDZ data types (e.g. sint) to make them compatible with oblif """
    tp.__and__ = tp.bit_and
    tp.__rand__ = tp.bit_and
    tp.__or__ = tp.bit_or
    tp.__ror__ = tp.bit_or
    tp.__deepcopy__ = lambda self, memo: self


