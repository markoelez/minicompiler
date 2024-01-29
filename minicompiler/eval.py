#!/usr/bin/env python3
from minicompiler.compiler.main import compile  # pylint: disable=redefined-builtin
from minicompiler.assembler.tokenizer import tokenize
from minicompiler.assembler.main import Assembler


if __name__ == '__main__':

    s = '''
    int _start() {
        int x = 3;
        int result = x + 42;
        return result;
    }
    '''

    # raw C program
    print(s)
    print('*' * 80)

    # C program -> ARM assembly IR (compilation)
    asm = compile(s)

    print(asm)
    print('*' * 80)

    # ASM assembly -> ASM tokens TODO: condense
    tokens = tokenize(asm)

    for x in tokens: print(x)
    print('*' * 80)

    # ASM tokens -> binary
    o = 'tmp9.o'
    Assembler(tokens).dump(o)
