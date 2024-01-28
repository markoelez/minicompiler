#!/usr/bin/env python3
from copy import deepcopy
from collections import deque
from tokens import Tok, TokType
from tree import ASTNode, Root, Decl, NumExpr, DeclRefExpr, ParenExpr, Expr, ReturnStmt, VarDecl, BinOp, FunctionDecl, AddOp, DeclStmt
from contextlib import contextmanager


class Parser:
    def __init__(self, tokens: list[Tok]):
        self.tokens = deque(tokens)

        self.dtypes = {TokType.INT, TokType.BOOL}

    @contextmanager
    def _preserving_state(self):
        q = deepcopy(self.tokens)
        try:
            yield
        except ValueError:
            self.tokens = q
        except Exception as e:
            print(e)
            raise

    def _test(self, f=lambda _: True, i: int = 0):
        return self.tokens and len(self.tokens) >= i + 1 and f(self.tokens[i])

    def _consume(self, f=lambda _: True):
        assert self._test(f)
        return self.tokens.popleft()

    def build(self) -> ASTNode:
        root = self._parse_root()
        return root

    # *************** AST utils ***************

    def _parse_root(self) -> Root:
        root = Root()

        while self._test():
            with self._preserving_state():
                root.children.append(self._parse_statement())
            with self._preserving_state():
                root.children.append(self._parse_declaration())

        return root

    # *************** expressions ***************

    def _parse_expr(self) -> Expr:

        root = Expr()

        binops = {
            TokType.PLUS: AddOp,
        }

        rterm = {TokType.SEMIC, TokType.RPAREN}

        # single number expression: i.e. '4;'
        def _parse_val() -> NumExpr | DeclRefExpr:
            if self._test(lambda x: x.type == TokType.NUM):
                return NumExpr(val=int(self._consume().data))
            if self._test(lambda x: x.type == TokType.IDENT):
                return DeclRefExpr(ident=self._consume().data)
            raise ValueError()

        # binary operation expression: i.e. '1 + 3'
        def _parse_binary_operation() -> BinOp | NumExpr | DeclRefExpr:
            op1 = _parse_val()
            if self._test(lambda x: x.type in rterm): return op1
            cls = binops[self._consume(lambda x: x.type in binops).type]
            root = cls(op1=op1)
            root.op2 = _parse_binary_operation()
            return root

        while self._test(lambda x: x.type not in rterm):
            if self._test(lambda x: x.type in binops, i=1):
                root = _parse_binary_operation()
            elif self._test(lambda x: x.type in rterm, i=1):
                root = _parse_val()
            elif self._test(lambda x: x.type == TokType.LPAREN):
                root = self._parse_paren_expr()

        self._consume(lambda x: x.type in rterm)
        return root

    def _parse_paren_expr(self) -> ParenExpr:
        self._consume(lambda x: x.type == TokType.LPAREN)
        root = ParenExpr()
        root.expr = self._parse_expr()
        return root

    # *************** declarations ***************

    def _parse_declaration(self) -> Decl:
        # function
        if self._test(lambda x: x.type == TokType.LPAREN, i=2):
            return self._parse_function()
        raise ValueError()

    def _parse_function(self) -> FunctionDecl:
        root = FunctionDecl()

        def _parse_args():
            res = []
            while self._test(lambda x: x.type != TokType.RPAREN):
                arg = VarDecl()
                arg.type = self._consume(lambda x: x.type in self.dtypes).data
                arg.ident = self._consume(lambda x: x.type == TokType.IDENT).data
                res.append(arg)
                if self._test(lambda x: x.type == TokType.COMMA): self._consume()
            return res

        def _parse_body():
            body = []
            while self._test(lambda x: x.type != TokType.RBRACE):
                if self._test(lambda x: x.type == TokType.ReturnStmt):
                    body.append(self._parse_return())
                    break
                s = self._parse_statement()
                body.append(s)
                if isinstance(s, ReturnStmt): break
            return body

        root.rtype = self._consume(lambda x: x.type in self.dtypes)
        root.ident = self._consume(lambda x: x.type == TokType.IDENT).data
        self._consume(lambda x: x.type == TokType.LPAREN)
        root.args = _parse_args()
        self._consume(lambda x: x.type == TokType.RPAREN)
        self._consume(lambda x: x.type == TokType.LBRACE)
        root.body.stmts = _parse_body()
        self._consume(lambda x: x.type == TokType.RBRACE)
        return root

    # *************** statements ***************

    def _parse_statement(self):
        # return statement
        if self._test(lambda x: x.type == TokType.ReturnStmt):
            return self._parse_return()
        if self._test(lambda x: x.type == TokType.EQ, i=2):
            return self._parse_var_decl()

        raise ValueError()

    def _parse_return(self) -> ReturnStmt:
        self._consume(lambda x: x.type == TokType.ReturnStmt)
        root = ReturnStmt()
        root.expr = self._parse_expr()
        return root

    def _parse_var_decl(self) -> DeclStmt:
        root = DeclStmt()
        root.var.type = self._consume(lambda x: x.type in self.dtypes).data
        root.var.ident = self._consume(lambda x: x.type == TokType.IDENT).data
        self._consume(lambda x: x.type == TokType.EQ)
        root.var.val = self._parse_expr()
        return root
