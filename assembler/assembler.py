#!/usr/bin/env python3
import os
import sys
from tokenizer import tokenize, Directive, Label, BinaryOp, UnaryOp


def process(op):
    match op:
        case Directive():
            pass
        case Label():
            pass
        case BinaryOp():
            pass
        case UnaryOp():
            pass


if __name__ == '__main__':

    assert len(sys.argv) > 1

    p = sys.argv[1]

    assert p.endswith('.s')
    assert os.path.isfile(p)

    with open(p, 'r') as fp:

        s = fp.read().strip()

        tokens = tokenize(s)

        for x in tokens: print(x)
        print()

        for x in tokens: process(x)
