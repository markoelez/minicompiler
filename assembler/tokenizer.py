import re
from collections import deque
from dataclasses import dataclass


def lex(s: str) -> list[list[str]]:
    def tokenize(line):
        pattern = r'"[^"]*"|[^,\s]+'
        return re.findall(pattern, line)
    lines = re.sub(r'//.*', '', s).split('\n')
    return [tokenize(line) for line in lines if line.strip()]


@dataclass(frozen=True)
class Label:
    name: str


@dataclass(frozen=True)
class Directive:
    name: str
    subject: str


@dataclass(frozen=True)
class BinaryOp:
    name: str
    s1: str
    s2: str


@dataclass(frozen=True)
class UnaryOp:
    name: str
    s1: str


class Parser:
    def __init__(self, tokens: list[list[str]]):
        self.tokens = tokens
        self.q = deque(tokens)
        self.out = []

    def _test(self, f=lambda _: True):
        return self.q and f(self.q[0])

    def _consume(self, f=lambda _: True):
        assert self._test(f)
        return self.q.popleft()

    def _directive(self):
        name, sub = self._consume()
        self.out.append(Directive(name, sub))

    def _label(self):
        name = self._consume()[0]
        self.out.append(Label(name))

    def _statement(self):
        if self._test(lambda x: len(x) == 3):
            name, s1, s2 = self._consume()
            self.out.append(BinaryOp(name, s1, s2))
        elif self._test(lambda x: len(x) == 2):
            name, s1 = self._consume()
            self.out.append(UnaryOp(name, s1))

    def _line(self):
        if self._test(lambda x: x[0].startswith('.')):
            return self._directive()
        if self._test(lambda x: x[0].endswith(':')):
            return self._label()
        return self._statement()

    def parse(self):
        while self._test(): self._line()
        return self.out


def tokenize(asm: str):

    a = lex(asm)

    return Parser(a).parse()
