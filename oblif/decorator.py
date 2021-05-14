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
    for i in instrs: print("          ", retcurdepth, i)
        
    for i in instrs:
        if isinstance(i, Instr):
            if i.has_jump(): retdepths[id(i.arg)] = retcurdepth + i.stack_effect(True)
            if i.is_uncond_jump():
                retcurdepth = None
            else:
                retcurdepth += i.stack_effect(False)
        elif isinstance(i, Label):
            if retcurdepth is not None and retcurdepth != retdepths[id(i)]:
                raise RuntimeError("inconsistent depths for label", i)
            retcurdepth = retdepths[id(i)]
    
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
            Instr("BUILD_TUPLE", nstack, lineno=lineno),
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

def _oblif(code):
    """ Turn given code into data-oblivious code """
    doprint = os.getenv("OBLIV_VERBOSE", "0")=="1"
    
    bc = Bytecode.from_code(code)
    blocks = ControlFlowGraph.from_bytecode(bc)
    
    lineno = get_lineno(bc, 0)
    newcode = []
    add_to_code(newcode, init_code(lineno))
    for nm in bc.argnames:
        add_to_code(newcode, callcontext("set", 0, [nm, Instr("LOAD_FAST", nm, lineno = lineno)], 0, lineno))
                
                #[ins for nm in bc.argnames for ins in storeinctx(nm, lineno)])
    
    stack_sizes = {}
    stack_sizes[0] = 0              # stack size at start of block with given index 

    for block in blocks:
        # invariant: stack is empty if we enter, context has stored stack
        
        
        bix = blocks.get_block_index(block)
        print("[" + str(stack_sizes[bix]) + "] Block #%s" % (bix))
        
        label_start = Label()
        
        add_to_code(newcode,
            [label_start] +
            callcontext("label", 0, [bix,stack_sizes[bix]], 
                        (stack_sizes[bix],) if stack_sizes[bix]>0 else 1, block[0].lineno)
            # returns False if label should not be executed
            # otherwise True for an empty stack or (stackvalues,) for a non-empty stack
                    
        )
#            newcode.extend([label_at[ix]] + callargjif("label", labels[label_at[ix]], nextlabel, curlno))
#            if ssizes[ix]!=0: newcode.extend(callunstack("unstack", ssizes[ix], curlno))
        
        
        for instr in block:
            
            
            
            
            
            if isinstance(instr.arg, BasicBlock):
                arg = "<block #%s>" % (blocks.get_block_index(instr.arg))
            elif instr.arg is not UNSET:
                arg = repr(instr.arg)
            else:
                arg = ''
            print("    %s %s" % (instr.name, arg))

        if block.next_block is not None:
            #stack_sizes[blocks.get_block_index(block.next_block)] =
            print("    => <block #%s>"
                  % (blocks.get_block_index(block.next_block)))
            
        print()
            
        (effect_nojump,effect_jump) = block_stack_effects(block)
        
        if block.next_block is not None:
            bix2 = blocks.get_block_index(block.next_block)
            ss2 = stack_sizes[bix] + effect_nojump
            if bix2 in stack_sizes and stack_sizes[bix2]!=ss2:
                raise ValueError("inconsistent stack depth at", bix2, "from", bix, ":", stack_sizes[bix2], ss2)
            stack_sizes[bix2] = ss2
            
        if (target:=block.get_jump()) is not None:
            bix2 = blocks.get_block_index(target)
            ss2 = stack_sizes[bix] + effect_jump
            if bix2 in stack_sizes and stack_sizes[bix2]!=ss2:
                raise ValueError("inconsistent stack depth at", bix2, "from", bix, ":", stack_sizes[bix2], ss2)
            stack_sizes[bix2] = ss2
            
    
    labels = {}                      # given Label, gives number for it
    last_backjump_per_label = {}     # given Label, give index of last instruction jumping back to it
    label_at = {}                    # given index, give label at that index
    backjump_to = {}                 # given index, give label to which this index is the last jump instruction
    

    
#    print("***")
#    for (ix,i) in enumerate(bc):
#        print(ix, "*", instrstring(bc, i))
#    print("***")
    

    
    # make scan through code:
    # - number labels
    # - keep track of last jump back to a label, ensure that this is consistent
    # - for each instruction representing a jump, ensure that nextlabel is set
    
#    print("*** static analysis")

    ssizes = compute_stack_sizes(bc)

#    print("ssizes", ssizes)

    #    if instrs[ix].has_jump(): raise RuntimeError("unexpected jump")
    #    print(ix, instrs[ix], depth)
    #    depth += instrs[ix].stack_effect()
    
    for (ix,instr) in enumerate(bc):
        if isinstance(instr,Label):
            labels[instr] = ix
            label_at[ix] = instr
            
        if isinstance(instr, Instr) and instr.name in jumpinstrs and \
           not(ix+1<len(bc) and isinstance(bc[ix+1],Label)):
            lab = Label()
            labels[lab] = ix+1
            label_at[ix+1] = lab
        
        if isinstance(instr, Instr) and instr.name in jumpinstrs and instr.arg in labels:
            if instr.arg in last_backjump_per_label:
                del backjump_to[last_backjump_per_label[instr.arg]]
            last_backjump_per_label[instr.arg] = ix
            backjump_to[ix] = instr.arg
            
    for (ix,instr) in enumerate(bc):
        if ix in label_at and label_at[ix] in last_backjump_per_label:
            for ix2 in range(ix+1, last_backjump_per_label[label_at[ix]]):
                if ix2 in label_at and label_at[ix2] in last_backjump_per_label:
#                    print("*** checking loop consistancy")
                    if not (ix+1<=last_backjump_per_label[label_at[ix2]]<last_backjump_per_label[label_at[ix]]):
                        raise RuntimeError("inconsistent loops")
                        
    for ix in backjump_to:
        if ix not in label_at:
            # create label at the backjump so we will reach it
#            print("creating label at", ix)
            lab = Label()
            labels[lab] = ix
            label_at[ix] = lab
    
#    print("*** static analysis done")
    
#    print("backjump to", backjump_to)

    label_ret = Label()
    label_ret_ix = len(bc)
    
    for (ix,instr) in enumerate(bc):
        curlno = get_lineno(bc, ix)
#        print("lineno", curlno)
        
        if ix in label_at:
#            print("label at", ix, label_at, last_backjump_per_label)
            if label_at[ix] in last_backjump_per_label:
                # this is a while loop, if we don't want to do it, jump to its end
                ix2 = last_backjump_per_label[label_at[ix]]+1
#                print("while loop, next is", ix2)
            else:
                # find next label
                ix2 = ix+1
                while (not ix2 in label_at) and ix2<len(bc): ix2+=1 
#                print("not a while loop, next is", ix2)
                
            nextlabel = label_ret if ix2==len(bc) else label_at[ix2]
            #lineno = get_lineno(bc, ix)
            
            if not isinstance(bc[ix-1],Instr) or (not bc[ix-1].has_jump() and not bc[ix-1].name=="RETURN_VALUE" and not bc[ix-1].name=="FOR_ITER" and ssizes[ix]!=0):
                # if previous block does not end with a jump, we have to manually stack up ourselves
                # TODO: more generic
                newcode.extend(callstack("stack", ssizes[ix], curlno))
            newcode.extend([label_at[ix]] + callargjif("label", labels[label_at[ix]], nextlabel, curlno))
            if ssizes[ix]!=0: newcode.extend(callunstack("unstack", ssizes[ix], curlno))
                
        if not isinstance(instr, Instr): continue
            
        if instr.name=="STORE_FAST" and instr.arg[-1]!="_":
            newcode.extend(callset(instr.arg, curlno))
        elif (instr.name=="LOAD_FAST" and instr.arg[-1]!="_") or (instr.name=="LOAD_GLOBAL" and instr.arg=="__guard"):
            newcode.extend(callget(instr.arg, curlno))
        elif instr.name=="LOAD_GLOBAL" and instr.arg=="range":
            patch_range(bc,ix)
            newcode.append(bc[ix])
        elif instr.name=="GET_ITER":
            newcode.extend(callstack1("getiter", curlno))
        elif instr.name=="FOR_ITER":                                    # stack = X|iter
            newcode.extend([
                 Instr("DUP_TOP", lineno=curlno),                 # stack = X|iter|iter
                 Instr("LOAD_METHOD", "__next__", lineno=curlno), # stack = X|iter|iter|__iter__
                 Instr("CALL_METHOD", 0, lineno=curlno),          # stack = X|iter|(val,cond)
                 Instr("UNPACK_SEQUENCE", 2, lineno=curlno)] +    # stack = X|iter|val|cond
                 callstackargs("pjif", ssizes[ix]+2, labels[instr.arg], lineno=curlno))
#                
#            label_nxt = Label()
#            label_after = Label()
#            newcode.extend(
#                [Instr("FOR_ITER", label_nxt),
#                 Instr("JUMP_FORWARD", label_after),
#                 label_next] + 
#                 newcode.extend(callstack("stack", ssizes[ix]-1, lineno)) +
#                [Instr("JUMP_ABSOLUTE", )]
#                 
#                    "DUP_TOP", lineno=curlno),                 # stack = X|iter|iter
#                 Instr("LOAD_METHOD", "__iter__", lineno=curlno), # stack = X|iter|iter|__iter__
#                 Instr("CALL_METHOD", 0, lineno=curlno),          # stack = X|iter|(val,cond)
#                 Instr("UNPACK_SEQUENCE", 2, lineno=curlno)]      # stack = X|iter|val|cond
#                 + callstackargs("pjif", ssizes[ix]+2, labels[instr.arg], lineno=curlno))
#            
#            print("stack size at iter", ssizes[ix])
#            newcode.extend(                                           
#                [instr,                                               # stack = X|iter|(val,cond)
#                 Instr("UNPACK_SEQUENCE", 2, lineno=curlno)] +  # stack = X|iter|val|cond
#                 callstackargs("pjif", ssizes[ix]+2, labels[instr.arg], lineno=curlno) +
#                 callunstack("unstack", ssizes[ix]+1, lineno=curlno))
            # note that iter|val|cond should not be on the stack after the loop, but since
            # this context will be merged with a context that doesn't have them, they will
            # be thrown away anyway
        elif instr.name=="POP_JUMP_IF_FALSE":
            #if ssizes[ix]!=1: raise RuntimeError("extra stack depth at jump @" + str(ix))
            newcode.extend(callstackargs("pjif", ssizes[ix], labels[instr.arg], lineno=curlno))
        elif instr.name=="POP_JUMP_IF_TRUE":
            if ssizes[ix]!=1: raise RuntimeError("extra stack depth at jump @" + str(ix))
            newcode.extend(callstackargs("pjit", ssizes[ix], labels[instr.arg], lineno=curlno))
        elif instr.name=="JUMP_ABSOLUTE":
            #if ssizes[ix]!=0: raise RuntimeError("nonzero stack depth at jump @" + str(ix))
            newcode.extend(callstackargs("jmp", ssizes[ix], labels[instr.arg], lineno=curlno))
        elif instr.name=="JUMP_FORWARD":
            newcode.extend(callstackargs("jmp", ssizes[ix], labels[instr.arg], lineno=curlno))
            #if ssizes[ix]==0:
            #    newcode.extend(callarg("jmp", labels[instr.arg], lineno=curlno))
            #elif ssizes[ix]==1: # jump as part of a ternary operator
            #    newcode.extend(callset("__stack", lineno=curlno))
            #    newcode.extend(callarg("jmp", labels[instr.arg], lineno=curlno))
            #else:
            #    raise RuntimeError("nonzero stack depth at jump @" + str(ix))
        elif instr.name=="RETURN_VALUE":
            if ssizes[ix]!=1: raise RuntimeError("unexpected stack elements on return @" + str(ix))
            newcode.extend(callstackarg("ret", label_ret_ix, lineno=curlno))
        elif instr.name=="JUMP_IF_TRUE_OR_POP":
            raise RuntimeError("JUMP_IF_TRUE_OR_POP not supported @" + str(curlno))
        elif instr.name=="JUMP_IF_FALSE_OR_POP":
            raise RuntimeError("JUMP_IF_FALSE_OR_POP not supported @" + str(curlno))
        else:
            newcode.append(instr)
            
        if ix in backjump_to:
            newcode.append(Instr("JUMP_ABSOLUTE", backjump_to[ix]))
            

#    # TODO: may be needed?
#    if isinstance(bc[len(bc)-1],Instr) and not bc[len(bc)-1].has_jump() and not bc[ix-1].name=="RETURN_VALUE":
#        newcode.extend(callstack("stack", 1, bc[len(bc)-1].lineno))
    newcode.extend([label_ret] + 
                   callarg("label", label_ret_ix, lineno) +
                   callunstack("unstack", 1, lineno) + 
                   [Instr("RETURN_VALUE")])
                   #callargnopop("doret", label_ret_ix, bc[len(bc)-1].lineno) + [Instr("RETURN_VALUE")])
            #newcode.extend([label_at[ix]] + callargjif("label", labels[label_at[ix]], nextlabel, lineno))
            
            
    bc.clear()
    for bci in newcode: bc.append(bci)
        
#    print("***")
#    for (ix,i) in enumerate(bc):
#        print("*", ix, "*", newsz[ix], "*", instrstring(bc, i))
#    print("***")        
#        
    newsz = compute_stack_sizes(bc)
        
#    print("***")
#    for (ix,i) in enumerate(bc):
#        print("*", ix, "*", newsz[ix], "*", instrstring(bc, i))
#    print("***")        
#    
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
