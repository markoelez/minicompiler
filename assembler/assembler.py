#!/usr/bin/env python3
import os
import sys
import re
import struct
from dataclasses import dataclass
from enum import Enum
from collections import deque
from macho import write_macho


def strip_comments(s): return s.split('//')[0].strip()


def lex(s: str) -> list[list[str]]:
    a = [strip_comments(x) for x in s.split('\n')]
    def p(a): return [x.strip() for x in a.split() if x]
    a = [p(x) for x in a if p(x)]
    return a


class Parser:
    def __init__(self, tokens: list[list[str]]):
        self.tokens = deque(tokens)
        self.st = {}

    def _test(self, f: lambda: True):
        return self.tokens and f(self.tokens[0])

    def _consume(self, f: lambda: True):
        assert self.test(self.tokens, f)
        return self.tokens.popleft()

    def _line(self, s: str):
        pass

    def parse(self):
        for x in self.tokens: self._line(x)


if __name__ == '__main__':

    # assert len(sys.argv) > 1

    # p = sys.argv[1]

    # assert p.endswith('.s')
    # assert os.path.isfile(p)

    # with open(p, 'r') as fp:

    #     s = fp.read().strip()

    #     a = lex(s)

    #     Parser(a).parse()

    outfile = 'out.o'

    write_macho(outfile)
