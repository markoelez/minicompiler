#!/usr/bin/env python3
from lexer import lex
from parser import Parser  # pylint: disable=deprecated-module


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

    # parse: list[Tok] -> AST
    Parser(a).build()
