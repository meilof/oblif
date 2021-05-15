import os
import functools
import types

from bytecode import UNSET, Label, Instr, Bytecode, BasicBlock, ControlFlowGraph

def init_code(lineno):
    return [ # creation of context
        Instr("LOAD_CONST", 0, lineno = lineno),
        Instr("LOAD_CONST",  None, lineno = lineno),
        Instr("IMPORT_NAME",  'oblif.context', lineno = lineno),
        Instr("STORE_FAST",  'oblif', lineno = lineno),
        Instr("LOAD_FAST",  'oblif', lineno = lineno),
        Instr("LOAD_ATTR",  'context', lineno = lineno),
        Instr("LOAD_METHOD",  'Ctx', lineno = lineno),
        Instr("CALL_METHOD",  0, lineno = lineno),
        Instr("STORE_FAST",  'ctx', lineno = lineno)
    ]
#        Instr("LOAD_CONST", 0, lineno = lineno),
#        Instr("LOAD_CONST", None, lineno = lineno),
#        Instr("IMPORT_NAME", "context", lineno = lineno),
#        Instr("LOAD_METHOD", "Ctx", lineno = lineno),
#        Instr("CALL_METHOD", 0, lineno = lineno),
#        Instr("STORE_FAST", "ctx", lineno = lineno),
#    ]

def callstack1(fn, lineno):
    return \
        [Instr("LOAD_FAST", "ctx", lineno=lineno), 
         Instr("LOAD_METHOD", fn, lineno=lineno),
         Instr("ROT_THREE", lineno=lineno), 
         Instr("ROT_THREE", lineno=lineno), 
         Instr("CALL_METHOD", 1, lineno=lineno)]   

def callset(var, lineno):
    return \
        [Instr("LOAD_FAST", "ctx", lineno=lineno), 
         Instr("LOAD_METHOD", "set", lineno=lineno),
         Instr("LOAD_CONST", var, lineno=lineno),
         Instr("ROT_FOUR", lineno=lineno), 
         Instr("ROT_FOUR", lineno=lineno), 
         Instr("ROT_FOUR", lineno=lineno), 
         Instr("CALL_METHOD", 2, lineno=lineno),
         Instr("POP_TOP", lineno=lineno)]    

def callget(var, lineno):
    return \
        [Instr("LOAD_FAST", "ctx", lineno=lineno),
         Instr("LOAD_METHOD", "get", lineno=lineno),
         Instr("LOAD_CONST", var, lineno=lineno), 
         Instr("CALL_METHOD", 1, lineno=lineno)]        
    
def storeinctx(nm, lineno):
    return [ # variable initialization
        Instr("LOAD_FAST", "ctx", lineno = lineno),
        Instr("LOAD_METHOD", "set", lineno = lineno),
        Instr("LOAD_CONST", nm, lineno = lineno),
        Instr("LOAD_FAST", nm, lineno = lineno),
        Instr("CALL_METHOD", 2, lineno = lineno),
        Instr("POP_TOP", lineno = lineno)
    ]

def callstack(meth, nstack, lineno):
    return [
        Instr("BUILD_TUPLE", nstack, lineno = lineno),
        Instr("LOAD_FAST", "ctx", lineno = lineno),
        Instr("LOAD_METHOD", meth, lineno = lineno),
        Instr("ROT_THREE", lineno = lineno),
        Instr("ROT_THREE", lineno = lineno),
        Instr("CALL_METHOD", 1, lineno = lineno),
        Instr("POP_TOP", lineno = lineno)
    ]


def callstackarg(meth, arg, lineno):
    return [
        Instr("LOAD_FAST", "ctx", lineno = lineno),
        Instr("LOAD_METHOD", meth, lineno = lineno),
        Instr("ROT_THREE", lineno = lineno),
        Instr("ROT_THREE", lineno = lineno),
        Instr("LOAD_CONST", arg, lineno = lineno),
        Instr("CALL_METHOD", 2, lineno = lineno),
        Instr("POP_TOP", lineno = lineno)
    ]

def callstackargs(meth, nstack, arg, lineno):
    return [
        Instr("BUILD_TUPLE", nstack, lineno = lineno),
        Instr("LOAD_FAST", "ctx", lineno = lineno),
        Instr("LOAD_METHOD", meth, lineno = lineno),
        Instr("ROT_THREE", lineno = lineno),
        Instr("ROT_THREE", lineno = lineno),
        Instr("LOAD_CONST", arg, lineno = lineno),
        Instr("CALL_METHOD", 2, lineno = lineno),
        Instr("POP_TOP", lineno = lineno)
    ]

def callunstack(meth, nstack, lineno):
    return [
        Instr("LOAD_FAST", "ctx", lineno = lineno),
        Instr("LOAD_METHOD", meth, lineno = lineno),
        Instr("LOAD_CONST", nstack, lineno = lineno),
        Instr("CALL_METHOD", 1, lineno = lineno),
        Instr("UNPACK_SEQUENCE", nstack, lineno = lineno),
    ]

def callargnopop(meth, arg, lineno):
    return [
        Instr("LOAD_FAST", "ctx", lineno = lineno),
        Instr("LOAD_METHOD", meth, lineno = lineno),
        Instr("LOAD_CONST", arg, lineno = lineno),
        Instr("CALL_METHOD", 1, lineno = lineno),
    ]

def callargjif(meth, arg, label, lineno):
    return [
        Instr("LOAD_FAST", "ctx", lineno = lineno),
        Instr("LOAD_METHOD", meth, lineno = lineno),
        Instr("LOAD_CONST", arg, lineno = lineno),
        Instr("CALL_METHOD", 1, lineno = lineno),
        Instr("POP_JUMP_IF_FALSE", label, lineno = lineno)
    ]

def callarg(meth, arg, lineno):
    return [
        Instr("LOAD_FAST", "ctx", lineno = lineno),
        Instr("LOAD_METHOD", meth, lineno = lineno),
        Instr("LOAD_CONST", arg, lineno = lineno),
        Instr("CALL_METHOD", 1, lineno = lineno),
        Instr("POP_TOP", lineno = lineno)
    ]

jumpinstrs = { "JUMP_FORWARD", "JUMP_ABSOLUTE", "POP_JUMP_IF_FALSE", "POP_JUMP_IF_TRUE", "RETURN_VALUE", "FOR_ITER" }


        
def compute_stack_sizes(bc):
    ssizes = {0:0}
    for (ix,instr) in enumerate(bc):
#        print(ix, "*", ssizes[ix], "*", instrstring(bc,instr))
        
        if isinstance(instr, Label):
            ssizes[ix+1] = ssizes[ix]
            continue
        
        nextsize = ssizes[ix] + instr.stack_effect()
        if instr.has_jump():
            nextsize2 = nextsize if instr.name!="FOR_ITER" else nextsize-2
            ix2 = bc.index(instr.arg)
            if ix2 in ssizes and ssizes[ix2]!=nextsize2:
                raise RuntimeError("inconsistent stack depth at #" + str(ix2) + ": " + 
                                   str(nextsize2) + " vs " + str(ssizes[ix2]))
            ssizes[ix2] = nextsize2
        if not instr.is_uncond_jump():
            ssizes[ix+1] = nextsize
            
    return ssizes
            
    

def get_lineno(bc, ix):
    if isinstance(bc[ix], Instr): return bc[ix].lineno
    ixl = ix+1
    while ixl<len(bc) and not isinstance(bc[ixl], Instr): ixl+=1
    return bc[ixl].lineno

def instrstring(bc, instr):
    if isinstance(instr, Instr) and instr.has_jump():
        return str(instr) + " => " + str(bc.index(instr.arg))
    return str(instr)

def block_stack_effects(block):
    return (sum([i.stack_effect(False) for i in block]), 
            sum([i.stack_effect(True) for i in block]))


retcurdepth = 0
retdepths = {}

def add_to_code(lst, instrs):
    global retcurdepth
    global retdepths
    
    lst.extend(instrs)
        
    for i in instrs:
        if isinstance(i, Instr):
            # instruction: retcurdepth is OK
            print("          ", retcurdepth, i, end=' -> ')
            if i.has_jump(): retdepths[id(i.arg)] = retcurdepth + i.stack_effect(True)
            if i.is_uncond_jump():
                retcurdepth = None
            else:
                retcurdepth += i.stack_effect(False)
        elif isinstance(i, Label):
            # label: check compute retcurdepth
            if retcurdepth is None:
                if id(i) not in retdepths: raise RuntimeError("unreachable code")
                retcurdepth = retdepths[id(i)]
            elif id(i) in retdepths and retcurdepth != retdepths[id(i)]:
                raise RuntimeError("inconsistent depths for label", i)
            print("          ", retcurdepth, i, end=' -> ')
        print(retcurdepth)
    
""" Return code for calling a context function, stack can be 0, 1, or (n), args can be a list, ret can be 0, 1, or (n) """
def callcontext(fn, stack, args, rets, lineno):
    ret = []
    
    if stack==0:
        ret.extend([
            Instr("LOAD_FAST", "ctx", lineno=lineno),
            Instr("LOAD_METHOD", fn, lineno=lineno),
        ])
    elif stack==1:
        ret.extend([
            Instr("LOAD_FAST", "ctx", lineno=lineno),
            Instr("LOAD_METHOD", fn, lineno=lineno),
            Instr("ROT_THREE", lineno=lineno),
            Instr("ROT_THREE", lineno=lineno),        
        ])
    elif isinstance(stack,tuple) and len(stack)==1:
        ret.extend([
            Instr("BUILD_TUPLE", stack[0], lineno=lineno),
            Instr("LOAD_FAST", "ctx", lineno=lineno),
            Instr("LOAD_METHOD", fn, lineno=lineno),
            Instr("ROT_THREE", lineno=lineno),
            Instr("ROT_THREE", lineno=lineno),
        ])
    else:
        raise RuntimeError("unexpected stack value: " + repr(stack))
        
    for arg in args: 
        if isinstance(arg, Instr):
            ret.append(arg)
        else:
            ret.append(Instr("LOAD_CONST", arg, lineno=lineno))
            
    ret.append(Instr("CALL_METHOD", len(args)+(0 if stack==0 else 1), lineno=lineno))
    
    if rets==0:
        ret.append(Instr("POP_TOP", lineno=lineno))
    elif rets==1:
        pass
    elif isinstance(rets,tuple):
        ret.append(Instr("UNPACK_SEQUENCE", rets[0], lineno = lineno)),
    else:
        raise RuntimeError("unexpected return value: " + repr(rets))
        
    return ret


def get_function_args(instrs, ix):
    ix+=1
    args = {}
    depth = 0
    
    while not (instrs[ix].name=="CALL_FUNCTION" and instrs[ix].arg==depth):
        if instrs[ix].has_jump(): raise RuntimeError("unexpected jump")
#        print(ix, instrs[ix], depth)
        depth += instrs[ix].stack_effect()
        args[depth] = ix
        ix += 1
        
#    print("args", args)
    return [args[d+1] for d in range(depth)]


def patch_range(instrs, ix):
#    print("patch range", ix, get_function_args(instrs, ix))
    
    args = get_function_args(instrs, ix)
    
#    print("found", args)
    
#    for i in range(ix, args[len(args)-1]+3):
#        print(i, instrs[i])
    
    if len(args)==1:
        # one function argument
        if instrs[ix+1].name=="LOAD_GLOBAL" and instrs[ix+1].arg=="min":
#            print("found")
            instrs[ix] = Instr("LOAD_FAST", "ctx")
            instrs[ix+1] = Instr("LOAD_METHOD", "range")
            instrs[args[0]] = Instr("NOP")
            instrs[args[0]+1] = Instr("CALL_METHOD", 2)
    elif len(args)==2 or len(args)==3:
        arg1s = args[0]+1
        arg2s = args[1]
        if instrs[arg1s].name=="LOAD_GLOBAL" and instrs[arg1s].arg=="min":
            for i in range(arg1s, ix, -1): instrs[i] = instrs[i-1]
            instrs[ix] = Instr("LOAD_FAST", "ctx")
            instrs[ix+1] = Instr("LOAD_METHOD", "range")
            instrs[arg2s] = Instr("NOP")
            instrs[args[len(args)-1]+1] = Instr("CALL_METHOD", len(args)+1)
            #instrs[arg1s+1] = 
            #instrs[arg2s-1]
    
#    print("after")
#    for i in range(ix, args[len(args)-1]+3):
#        print(i, instrs[i])

def _oblif(code):
    """ Turn given code into data-oblivious code """
    doprint = os.getenv("OBLIV_VERBOSE", "0")=="1"
    
    bc = Bytecode.from_code(code)
    blocks = ControlFlowGraph.from_bytecode(bc)
    
    # initialization code
    lineno = get_lineno(bc, 0)
    newcode = []
    add_to_code(newcode, init_code(lineno))
    for nm in bc.argnames:
        add_to_code(newcode, 
                    [Instr("LOAD_FAST", nm, lineno = lineno)] + callcontext("set", 1, [nm], 0, lineno))
    
    stack_sizes = {}                                  # stack size at start of block with given index 
    stack_sizes[0] = 0
    
    labels = [Label() for _ in range(len(blocks)+1)]  # label at start of a block
    
    last_backjump_to = {}                             # per block index: index of last block that jumps back to it
    for (bix,block) in enumerate(blocks):
        if (b:=block.get_jump()) is not None and (bix2:=blocks.get_block_index(b))<bix:
            last_backjump_to[bix2] = bix

    for (bix,block) in enumerate(blocks):
        # invariant: stack is empty if we enter, context has stored stack
        #bix = blocks.get_block_index(block)
        print("[" + str(stack_sizes[bix]) + "] Block #%s" % (bix))
        
        if (b:=block.get_jump()) is not None and \
           (bix2:=blocks.get_block_index(b))<bix and  \
           last_backjump_to[bix2]==bix:
            # last block of loop, need to jump back to beginning
            if bix in last_backjump_to: raise RuntimeError("block is both backjump and backjumped")
            nextlabel = Label()
            backjump_to = labels[bix2]
        elif bix in last_backjump_to:
            # first block of a loop, need to jump to end
            nextlabel = labels[last_backjump_to[bix]+1]
            backjump_to = None
        else:
            # normal block, jump to next
            nextlabel = labels[bix+1]
            backjump_to = None
            
        (effect_nojump,effect_jump) = block_stack_effects(block)
        
        if block.next_block is not None:
            bix2 = blocks.get_block_index(block.next_block)
            stack_size_nojump = stack_sizes[bix] + effect_nojump
            if bix2 in stack_sizes and stack_sizes[bix2]!=stack_size_nojump:
                raise ValueError("inconsistent stack depth at", bix2, "from", bix, ":", stack_sizes[bix2], stack_size_nojump)
            stack_sizes[bix2] = stack_size_nojump
            
        if (target:=block.get_jump()) is not None:
            bix2 = blocks.get_block_index(target)
            stack_size_jump = stack_sizes[bix] + effect_jump
            if bix2 in stack_sizes and stack_sizes[bix2]!=stack_size_jump:
                raise ValueError("inconsistent stack depth at", bix2, "from", bix, ":", stack_sizes[bix2], stack_size_jump)
            stack_sizes[bix2] = stack_size_jump
            
        if bix>0:
            add_to_code(newcode,
                [labels[bix]] +
                # returns False if label should not be executed
                # otherwise True for an empty stack or (stackvalues,) for a non-empty stack
                callcontext("label", 0, [bix,stack_sizes[bix]], 1, block[0].lineno) + [
                Instr("JUMP_IF_TRUE_OR_POP", lbl_aftercheck:=Label(), lineno=block[0].lineno),
                # if we are here, the False return of label has been popped
                Instr("JUMP_ABSOLUTE", nextlabel, lineno=block[0].lineno),
                lbl_aftercheck] +
                # if we are here, we have either True or a tuple of stack values
                ([Instr("UNPACK_SEQUENCE", stack_sizes[bix], lineno=block[0].lineno)] if stack_sizes[bix]>0 else
                 [Instr("POP_TOP", lineno=block[0].lineno)])
            )
        
        for (iix,instr) in enumerate(block):
            if isinstance(instr.arg, BasicBlock):
                arg = "<block #%s>" % (blocks.get_block_index(instr.arg))
            elif instr.arg is not UNSET:
                arg = repr(instr.arg)
            else:
                arg = ''
            print("    %s %s" % (instr.name, arg))
            
            if instr.name=="STORE_FAST" and instr.arg[-1]!="_":
                add_to_code(newcode,callcontext("set", 1, [instr.arg], 0, instr.lineno))
            elif (instr.name=="LOAD_FAST" and instr.arg[-1]!="_") or (instr.name=="LOAD_GLOBAL" and instr.arg=="__guard"):
                add_to_code(newcode,callcontext("get", 0, [instr.arg], 1, instr.lineno))
            elif instr.name=="LOAD_GLOBAL" and instr.arg=="range":
                patch_range(block,iix)
                add_to_code(newcode,[block[iix]])
            elif instr.name=="GET_ITER":
                add_to_code(newcode,callcontext("getiter", 1, [], 1, instr.lineno))
            elif instr.name=="FOR_ITER":                                    # stack = X|iter
                add_to_code(newcode, [
                     Instr("DUP_TOP", lineno=instr.lineno),                 # stack = X|iter|iter
                     Instr("LOAD_METHOD", "__next__", lineno=instr.lineno), # stack = X|iter|iter|__iter__
                     Instr("CALL_METHOD", 0, lineno=instr.lineno),          # stack = X|iter|(val,cond)
                     Instr("UNPACK_SEQUENCE", 2, lineno=instr.lineno)] +    # stack = X|iter|val|cond
                     callcontext("pjif", (stack_size_nojump+1,), [bix+1, blocks.get_block_index(instr.arg)], 0, instr.lineno))
                     #callstackargs("pjif", ssizes[ix]+2, , lineno=instr.lineno))
                # note that iter|val|cond should not be on the stack after the loop, but since
                # this context will be merged with a context that doesn't have them, they will
                # be thrown away anyway
            elif instr.name=="POP_JUMP_IF_FALSE":
                add_to_code(newcode,callcontext("pjif", (stack_size_nojump+1,), 
                                        [bix+1, blocks.get_block_index(instr.arg)], 0, lineno=instr.lineno))
            elif instr.name=="POP_JUMP_IF_TRUE":
                add_to_code(newcode,callcontext("pjit", (stack_size_nojump+1,), 
                                        [bix+1, blocks.get_block_index(instr.arg)], 0, lineno=instr.lineno))
            elif instr.name=="JUMP_ABSOLUTE":
                add_to_code(newcode,callcontext("jmp", (stack_size_jump,), 
                                        [blocks.get_block_index(instr.arg)], 0, lineno=instr.lineno))
            elif instr.name=="JUMP_FORWARD":
                add_to_code(newcode,callcontext("jmp", (stack_size_jump,), 
                                        [blocks.get_block_index(instr.arg)], 0, lineno=instr.lineno))
            elif instr.name=="RETURN_VALUE":
                #print("ret_val", stack_size_nojump)
                add_to_code(newcode,callcontext("ret", 1, [len(blocks)], 0, lineno=instr.lineno))
            elif instr.name=="JUMP_IF_TRUE_OR_POP":
                raise RuntimeError("JUMP_IF_TRUE_OR_POP not supported @" + str(curlno))
            elif instr.name=="JUMP_IF_FALSE_OR_POP":
                raise RuntimeError("JUMP_IF_FALSE_OR_POP not supported @" + str(curlno))
            else:
                add_to_code(newcode, [instr])
                
        #print("here", block.get_jump(), stack_size_nojump)
        if block.get_jump() is None and block[-1].name!="RETURN_VALUE":
            add_to_code(newcode,callcontext("jmp", (stack_size_nojump,), [bix+1], 0, lineno=instr.lineno))
            
            #add_to_code(newcode,callcontext("endblock", (stack_size_nojump,), [], 0, block[-1].lineno))
            
        if backjump_to is not None:
            add_to_code(newcode, [
                nextlabel, 
                Instr("JUMP_ABSOLUTE", backjump_to, lineno=block[-1].lineno)
            ])

        if block.next_block is not None:
            #stack_sizes[blocks.get_block_index(block.next_block)] =
            print("    => <block #%s>"
                  % (blocks.get_block_index(block.next_block)))
            
        print()
    
    add_to_code(newcode,
        [labels[len(blocks)]] + 
        callcontext("retlabel", 0, [len(blocks)], 1, blocks[-1][-1].lineno) +
        [Instr("RETURN_VALUE")])
            
    bc.clear()
    for bci in newcode: bc.append(bci)
        
    return bc.to_code()
        
def oblif(func_or_code):
    """ Turn given code or function into data-oblivious code/function """
    if isinstance(func_or_code, types.CodeType):
        return _oblif(func_or_code)
    
    return functools.update_wrapper(
        types.FunctionType(
            _oblif(func_or_code.__code__),
            func_or_code.__globals__,
            func_or_code.__name__,
            func_or_code.__defaults__,
            func_or_code.__closure__,
        ),
        func_or_code
    )
