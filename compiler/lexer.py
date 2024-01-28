#!/usr/bin/env python3
import re
from tokens import Tok, TokType


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
