import os
import functools
import types

from bytecode import UNSET, Label, Instr, Bytecode, BasicBlock, ControlFlowGraph

retcurdepth = 0
retdepths = {}

def add_to_code(lst, instrs):
    global retcurdepth
    global retdepths
    
    doprint = os.getenv("OBLIV_VERBOSE", "0")=="1"
    
    lst.extend(instrs)
        
    for i in instrs:
        if isinstance(i, Instr):
            # instruction: retcurdepth is OK
            if doprint: print("          ", retcurdepth, i, end=' -> ')
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
            if doprint: print("          ", retcurdepth, i, end=' -> ')
        if doprint: print(retcurdepth)
    
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


""" Turn given code into data-oblivious code """
def _oblif(code): 
    global retcurdepth
    global retdepths
    retcurdepth = 0
    retdepths = {}
    
    doprint = os.getenv("OBLIF_VERBOSE", "0")=="1"
    
    bc = Bytecode.from_code(code)
    blocks = ControlFlowGraph.from_bytecode(bc)
    
    # initialization code
    lineno = blocks[0][0].lineno
    newcode = []
    add_to_code(newcode, [
                    Instr("LOAD_CONST", 0, lineno = lineno),
                    Instr("LOAD_CONST",  None, lineno = lineno),
                    Instr("IMPORT_NAME",  'oblif.context', lineno = lineno),
                    Instr("STORE_FAST",  'oblif', lineno = lineno),
                    Instr("LOAD_FAST",  'oblif', lineno = lineno),
                    Instr("LOAD_ATTR",  'context', lineno = lineno),
                    Instr("LOAD_METHOD",  'Ctx', lineno = lineno),
                    Instr("CALL_METHOD",  0, lineno = lineno),
                    Instr("STORE_FAST",  'ctx', lineno = lineno)
    ])
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
        if doprint: print("[" + str(stack_sizes[bix]) + "] Block #%s" % (bix))
            
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
            
        if not bix in stack_sizes:
            # this looks like dead code, skip it
            # TODO: this cannot handel labels that can only be reached from later code,
            # does that ever happen?
            if bix in last_backjump_to: raise RuntimeError("block reachable only by back jump")
            add_to_code(newcode, [labels[bix]])
            if backjump_to is not None:
                add_to_code(newcode, [Instr("JUMP_ABSOLUTE", backjump_to, lineno=block[-1].lineno)])
            continue
            
        effect_nojump = sum([i.stack_effect(False) for i in block])
        effect_jump = sum([i.stack_effect(True) for i in block])
    
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
            if doprint: print("    %s %s" % (instr.name, arg))
            
            if instr.name=="STORE_FAST" and instr.arg[-1]!="_":
                add_to_code(newcode,callcontext("set", 1, [instr.arg], 0, instr.lineno))
            elif (instr.name=="LOAD_FAST" and instr.arg[-1]!="_") or (instr.name=="LOAD_GLOBAL" and instr.arg=="__guard"):
                add_to_code(newcode,callcontext("get", 0, [instr.arg], 1, instr.lineno))
            elif instr.name=="LOAD_GLOBAL" and instr.arg=="range":
                add_to_code(newcode,callcontext("range", 0, [], 1, instr.lineno))
#                add_to_code(newcode, [
#                        Instr("LOAD_FAST", "ctx", instr.lineno),
#                        Instr("LOAD_METHOD", "range", instr.lineno)
#                ])
                #patch_range(block,iix)
                #add_to_code(newcode,[block[iix]])
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
            if doprint: print("    => <block #%s>"
                  % (blocks.get_block_index(block.next_block)))
            
        if doprint: print()
    
    add_to_code(newcode,
        [labels[len(blocks)]] + 
        callcontext("label", 0, [len(blocks),1], 1, blocks[-1][-1].lineno) +
        [Instr("UNPACK_SEQUENCE", 1, lineno=block[0].lineno),
         Instr("RETURN_VALUE")])
            
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
