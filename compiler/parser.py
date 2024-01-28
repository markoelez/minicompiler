#!/usr/bin/env python3
from copy import deepcopy
from collections import deque
from lexer import Tok, TokType
from tree import ASTNode, ROOT, DECL, NUMBER, EXPR, RETURN, VAR, ADDITION, FUNC
from contextlib import contextmanager


class Parser:
    def __init__(self, tokens: list[Tok]):
        self.tokens = deque(tokens)

        for x in self.tokens: print(x)
        print('*' * 80)

    @contextmanager
    def _preserving_state(self):
        q = deepcopy(self.tokens)
        try:
            yield
        except AssertionError:
            raise
        except Exception:
            self.tokens = q

    def _test(self, f=lambda _: True, i: int = 0):
        return self.tokens and len(self.tokens) >= i + 1 and f(self.tokens[i])

    def _consume(self, f=lambda _: True):
        assert self._test(f)
        return self.tokens.popleft()

    def build(self) -> ASTNode:
        root = self._parse_root()
        return root

    # *************** AST utils ***************

    def _parse_root(self) -> ROOT:
        root = ROOT()

        while self._test():
            with self._preserving_state():
                root.children.append(self._parse_statement())
            with self._preserving_state():
                root.children.append(self._parse_declaration())

        root.print()

        return root

    # *************** expressions ***************

    def _parse_expr(self) -> EXPR:

        root = EXPR()

        # single number expression: i.e. '4;'
        def _parse_number() -> NUMBER:
            a = self._consume(lambda x: x.type == TokType.NUM)
            return NUMBER(val=int(a.data))

        # addition expression: i.e. '1 + 3'
        def _parse_addition() -> ADDITION:
            root = ADDITION()
            root.ops.append(_parse_number())
            while self._test(lambda x: x.type == TokType.PLUS):
                self._consume(lambda x: x.type == TokType.PLUS)
                root.ops.append(_parse_number())
            return root

        while self._test(lambda x: x.type != TokType.SEMIC):
            if self._test(lambda x: x.type == TokType.SEMIC, i=1):
                root = _parse_number()
            else:
                root = _parse_addition()

        self._consume(lambda x: x.type == TokType.SEMIC)
        return root

    # *************** declarations ***************

    def _parse_declaration(self) -> DECL:
        # function
        if self._test(lambda x: x.type == TokType.LPAREN, i=2):
            return self._parse_function()
        raise ValueError()

    def _parse_function(self) -> FUNC:
        root = FUNC()

        dtypes = {TokType.INT}

        def _parse_args():
            res = []
            while self._test(lambda x: x.type != TokType.RPAREN):
                arg = VAR()
                arg.type = self._consume(lambda x: x.type in dtypes).data
                arg.ident = self._consume(lambda x: x.type == TokType.IDENT).data
                res.append(arg)
                if self._test(lambda x: x.type == TokType.COMMA): self._consume()
            return res

        def _parse_body():
            body = []
            while self._test(lambda x: x.type != TokType.RBRACE):
                if self._test(lambda x: x.type == TokType.RETURN):
                    self._consume(lambda x: x.type == TokType.RETURN)
                    body.append(self._parse_return())
                    break
                s = self._parse_statement()
                body.append(s)
                if isinstance(s, RETURN): break
            return body

        root.rtype = self._consume(lambda x: x.type in dtypes)
        root.ident = self._consume(lambda x: x.type == TokType.IDENT).data
        self._consume(lambda x: x.type == TokType.LPAREN)
        root.args = _parse_args()
        self._consume(lambda x: x.type == TokType.RPAREN)
        self._consume(lambda x: x.type == TokType.LBRACE)
        root.body = _parse_body()
        self._consume(lambda x: x.type == TokType.RBRACE)
        return root

    # *************** statements ***************

    def _parse_statement(self):
        # return statement
        if self._test(lambda x: x.type == TokType.RETURN):
            self._consume(lambda x: x.type == TokType.RETURN)
            return self._parse_return()
        raise ValueError()

    def _parse_return(self) -> RETURN:
        root = RETURN()
        root.expr = self._parse_expr()
        return root
