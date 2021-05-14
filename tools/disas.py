from bytecode import Bytecode, ControlFlowGraph, dump_bytecode
from bytecode import UNSET, Label, Instr, Bytecode, BasicBlock, ControlFlowGraph

import types

def getfn(code, nm):
    for fs in code.co_consts:
        if isinstance(fs, types.CodeType) and fs.co_name==nm:
            return fs
    raise NameError("No such function: " + nm)

if __name__ == '__main__':
    lcode = compile(open("test2.py").read(), "test2.py", "exec", dont_inherit=True, optimize=0)

    #dis.dis(lcode)

    fn = getfn(lcode, "test")

    #https://stackoverflow.com/questions/16064409/how-to-create-a-code-object-in-python

    # print("argc", fn.co_argcount, file=sys.stderr) # number of args
    # print("kwonly", fn.co_kwonlyargcount, file=sys.stderr) # number of keyword-only arguments
    # print("nloc", fn.co_nlocals, file=sys.stderr) # number of local variables (vars, params except global names)
    # print("stack", fn.co_stacksize, file=sys.stderr) # stack required
    # print("flags", fn.co_flags, file=sys.stderr) # 1=optimized, 2=newlocals
    # print("consts", fn.co_consts, file=sys.stderr)
    # print("names", fn.co_names, file=sys.stderr)
    # print("varnames", fn.co_varnames, file=sys.stderr)
    # print("filename", fn.co_filename, file=sys.stderr)
    # print("name", fn.co_name, file=sys.stderr)
    # print("lineno", fn.co_firstlineno, file=sys.stderr)
    # print("lnotab", fn.co_lnotab, file=sys.stderr)
    # print("freevars", fn.co_freevars, file=sys.stderr)
    # print("cellvars", fn.co_cellvars, file=sys.stderr)
    # print("posonlyac", fn.co_posonlyargcount, file=sys.stderr)

    #print("# args:", " ".join(fn.co_varnames[:fn.co_argcount]))
    #print()

    bytecode = Bytecode.from_code(fn)
    blocks = ControlFlowGraph.from_bytecode(bytecode)
    #dump_bytecode(bytecode)
    

    for block in blocks:
        print("Block #%s" % (1 + blocks.get_block_index(block)))
        for instr in block:
            if isinstance(instr.arg, BasicBlock):
                arg = "<block #%s>" % (1 + blocks.get_block_index(instr.arg))
            elif instr.arg is not UNSET:
                arg = repr(instr.arg)
            else:
                arg = ''
            print("    %s %s" % (instr.name, arg))

        if block.next_block is not None:
            print("    => <block #%s>"
                  % (1 + blocks.get_block_index(block.next_block)))

        print()
