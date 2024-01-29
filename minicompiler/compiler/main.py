#!/usr/bin/env python3
from minicompiler.compiler.lexer import lex
from minicompiler.compiler.parser import Parser  # pylint: disable=deprecated-module
from minicompiler.compiler.tree import gen_asm


def read(path: str) -> str:
    fp = open(path, 'r')
    return fp.read().strip()


def compile(s: str, verbose: bool = False) -> str:  # pylint: disable=redefined-builtin

    # lex: str -> list[Tok]
    a = lex(s)

    #if verbose:
    #    for x in a: print(x)
    #    print('*' * 80)

    # parse: list[Tok] -> AST
    ast = Parser(a).build()

    if verbose:
        ast.print()
        print('*' * 80)

    # AST -> asm
    asm = gen_asm(ast)

    return asm


if __name__ == '__main__':
    '''
    str       -> list[Tok] (lex)
    list[Tok] -> AST       (parse)
    AST       -> ASM       (skip IR for now, otherwise AST -> IR -> ASM)
    '''

    fn = 'eval/test.c'

    s = read(fn)

    print(s)
    print('*' * 80)

    asm = compile(s)
    print(asm)
