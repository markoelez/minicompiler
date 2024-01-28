#!/usr/bin/env python3
import re
from enum import Enum
from dataclasses import dataclass


@dataclass(frozen=True)
class TokTypeVal:
    repr: str
    r: str


class TokType(Enum):
    # keywords
    INT = TokTypeVal('INT', 'int')
    BOOL = TokTypeVal('BOOL', 'bool')
    VOID = TokTypeVal('VOID', 'void')
    RETURN = TokTypeVal('RETURN', 'return')

    # block separators
    LPAREN = TokTypeVal('LPAREN', r'\(')
    RPAREN = TokTypeVal('RPAREN', r'\)')
    LBRACK = TokTypeVal('LRBACK', r'\[')
    RBRACK = TokTypeVal('RBRACK', r'\]')
    LBRACE = TokTypeVal('LBRACE', r'\{')
    RBRACE = TokTypeVal('RBRACE', r'\}')

    # logical separators
    COMMA = TokTypeVal('COMMA', r',')
    SEMIC = TokTypeVal('SEMICOLON', r';')
    PLUS = TokTypeVal('PLUS', r'\+')

    # atoms
    IDENT = TokTypeVal('IDENT', r'[_a-zA-Z][_a-zA-Z0-9]*')
    NUM = TokTypeVal('NUMBER', r'[0-9]+')
    DOT = TokTypeVal('DOT', r'\.')
    STR = TokTypeVal('STRING', r'"([^"\\]|\\.)*"')


@dataclass(frozen=True)
class Tok:
    type: TokType
    data: str | None

    def __repr__(self):
        return f'T(type=<TokType.{self.type.value.repr}>, data=\'{self.data}\')'


def lex(s: str) -> list[Tok]:

    h = {x.value.r: x for x in TokType}

    pt = re.compile('|'.join(h.keys()))

    res = []
    for m in re.finditer(pt, s):
        ms = m.group()

        for p, tok_type in h.items():
            if re.fullmatch(p, ms):
                tok = Tok(type=tok_type, data=ms)
                res.append(tok)
                break

    return res
