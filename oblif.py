import functools
import types

from bytecode import Label, Instr, Compare, Bytecode
        
def init_code(lineno):
    return [ # creation of context
        Instr("LOAD_CONST", 0, lineno = lineno),
        Instr("LOAD_CONST", None, lineno = lineno),
        Instr("IMPORT_NAME", "context", lineno = lineno),
        Instr("LOAD_METHOD", "Ctx", lineno = lineno),
        Instr("CALL_METHOD", 0, lineno = lineno),
        Instr("STORE_FAST", "ctx", lineno = lineno),
    ]

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


def callarg(meth, arg, lineno):
    return [
        Instr("LOAD_FAST", "ctx", lineno = lineno),
        Instr("LOAD_METHOD", meth, lineno = lineno),
        Instr("LOAD_CONST", arg, lineno = lineno),
        Instr("CALL_METHOD", 1, lineno = lineno),
        Instr("POP_TOP", lineno = lineno)
    ]

def callargjif(meth, arg, label, lineno):
    return [
        Instr("LOAD_FAST", "ctx", lineno = lineno),
        Instr("LOAD_METHOD", meth, lineno = lineno),
        Instr("LOAD_CONST", arg, lineno = lineno),
        Instr("CALL_METHOD", 1, lineno = lineno),
        Instr("POP_JUMP_IF_FALSE", label, lineno = lineno)
    ]


def get_function_args(instrs, ix):
    ix+=1
    args = {}
    depth = 0
    
    while not (instrs[ix].name=="CALL_FUNCTION" and instrs[ix].arg==depth):
        if instrs[ix].has_jump(): raise RuntimeError("unexpected jump")
        print(ix, instrs[ix], depth)
        depth += instrs[ix].stack_effect()
        args[depth] = ix
        ix += 1
        
    print("args", args)
    return [args[d+1] for d in range(depth)]


def patch_range(instrs, ix):
    print("patch range", ix, get_function_args(instrs, ix))
    
    args = get_function_args(instrs, ix)
    
    print("found", args)
    
    for i in range(ix, args[len(args)-1]+3):
        print(i, instrs[i])
    
    if len(args)==1:
        # one function argument
        if instrs[ix+1].name=="LOAD_GLOBAL" and instrs[ix+1].arg=="min":
            print("found")
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
    
    print("after")
    for i in range(ix, args[len(args)-1]+3):
        print(i, instrs[i])

jumpinstrs = { "JUMP_FORWARD", "JUMP_ABSOLUTE", "POP_JUMP_IF_FALSE", "POP_JUMP_IF_TRUE" }

labels = {}                      # given Label, gives number for it
last_backjump_per_label = {}     # given Label, give index of last instruction jumping back to it
label_at = {}                    # given index, give label at that index
backjump_to = {}                 # given index, give label to which this index is the last jump instruction

def get_lineno(bc, ix):
    ixl = ix+1
    while ixl<len(bc) and not isinstance(bc[ixl], Instr): ixl+=1
    return bc[ixl].lineno

def _oblif(code):
    global labels, last_backjump_per_label
    
    """ Turn given code into data-oblivious code """
    bc = Bytecode.from_code(code)
    
#    print("***")
#    for (ix,i) in enumerate(bc):
#        print(ix, "*", i)
#    print("***")
    
    lineno = get_lineno(bc, 0)
    newcode = init_code(lineno) + [ins for nm in bc.argnames for ins in storeinctx(nm, lineno)]
    
    # make scan through code:
    # - number labels
    # - keep track of last jump back to a label, ensure that this is consistent
    # - for each instruction representing a jump, ensure that nextlabel is set
    
#    print("*** static analysis")
    
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
    
    for (ix,instr) in enumerate(bc):
        
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
                
            if ix2<len(bc):
                newcode.extend([label_at[ix]] + callargjif("label", labels[label_at[ix]], label_at[ix2], get_lineno(bc, ix)))
            else:
                newcode.extend([label_at[ix]] + callarg("label", labels[label_at[ix]], get_lineno(bc, ix)))
        
        if not isinstance(instr, Instr): continue
            
        if instr.name=="STORE_FAST" and instr.arg!="ctx":
            newcode.extend(callset(instr.arg, instr.lineno))
        elif instr.name=="LOAD_FAST" and instr.arg!="ctx":
            newcode.extend(callget(instr.arg, instr.lineno))
        elif instr.name=="LOAD_GLOBAL" and instr.arg=="range":
            patch_range(bc,ix)
            newcode.append(bc[ix])
        elif instr.name=="FOR_ITER":
            newcode.extend(
                [Instr("DUP_TOP", lineno=instr.lineno)] + 
                callstackarg("foriter", labels[instr.arg], lineno=instr.lineno) +
                [instr])
        elif instr.name=="POP_JUMP_IF_FALSE":
            newcode.extend(callstackarg("pjif", labels[instr.arg], lineno=instr.lineno))
        elif instr.name=="POP_JUMP_IF_TRUE":
            newcode.extend(callstackarg("pjit", labels[instr.arg], lineno=instr.lineno))
        elif instr.name=="JUMP_ABSOLUTE":
            newcode.extend(callarg("jmp", labels[instr.arg], lineno=instr.lineno))
        elif instr.name=="JUMP_FORWARD":
            newcode.extend(callarg("jmp", labels[instr.arg], lineno=instr.lineno))
        elif instr.name=="JUMP_IF_TRUE_OR_POP":
            raise RuntimeError("JUMP_IF_TRUE_OR_POP not supported @" + str(instr.lineno))
        elif instr.name=="JUMP_IF_FALSE_OR_POP":
            raise RuntimeError("JUMP_IF_FALSE_OR_POP not supported @" + str(instr.lineno))
        else:
            newcode.append(instr)
            
        if ix in backjump_to:
            newcode.append(Instr("JUMP_ABSOLUTE", backjump_to[ix]))
            
    bc.clear()
    for bci in newcode: bc.append(bci)
        
        
#    print("***")
#    for i in bc:
#        print("*", i)
#    print("***")        
        
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
