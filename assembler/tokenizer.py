import re
from collections import deque
from assembler.tokens import Token, Directive, Label, MOV, ADR, SVC


def lex(s: str) -> list[list[str]]:
    def tokenize(line):
        pattern = r'"[^"]*"|[^,\s]+'
        return re.findall(pattern, line)
    lines = re.sub(r'//.*', '', s).split('\n')
    return [tokenize(line) for line in lines if line.strip()]


class Parser:
    def __init__(self, tokens: list[list[str]]):
        self.tokens: list[list[str]] = tokens
        self.q: deque[list[str]] = deque(tokens)
        self.out: list[Token] = []

    def _test(self, f=lambda _: True):
        return self.q and f(self.q[0])

    def _consume(self, f=lambda _: True):
        assert self._test(f)
        return self.q.popleft()

    def _directive(self):
        name, sub = self._consume()
        self.out.append(Directive(name, sub))

    def _label(self):
        name = self._consume()[0][:-1]
        self.out.append(Label(name))

    def _statement(self):
        ops = {
            'mov': MOV,
            'adr': ADR,
            'svc': SVC
        }
        if self._test(lambda x: len(x) == 3):
            name, s1, s2 = self._consume()
            self.out.append(ops[name](name, s1, s2))
        elif self._test(lambda x: len(x) == 2):
            name, s1 = self._consume()
            self.out.append(ops[name](name, s1))

    def _line(self):
        if self._test(lambda x: x[0].startswith('.')):
            return self._directive()
        if self._test(lambda x: x[0].endswith(':')):
            return self._label()
        return self._statement()

    def parse(self) -> list[Token]:
        while self._test(): self._line()
        return self.out


def tokenize(asm: str) -> list[Token]:

    a = lex(asm)

    return Parser(a).parse()
