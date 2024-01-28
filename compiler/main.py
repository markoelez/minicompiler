#!/usr/bin/env python3
from lexer import lex
from parser import Parser  # pylint: disable=deprecated-module
from tree import gen_asm


def read(path: str) -> str:
    fp = open(path, 'r')
    return fp.read().strip()


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

    # lex: str -> list[Tok]
    a = lex(s)

    for x in a: print(x)
    print('*' * 80)

    # parse: list[Tok] -> AST
    ast = Parser(a).build()

    ast.print()
    print('*' * 80)

    # AST -> asm
    asm = gen_asm(ast)

    print(asm)
    print('*' * 80)
