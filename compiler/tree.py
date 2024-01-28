from dataclasses import dataclass, field


class RegisterAllocator:
    def __init__(self):
        self.regs = {f'X{i}' for i in range(31)}

    def get_free(self) -> str:
        return self.regs.pop()


@dataclass
class ASTNode:

    is_leaf: bool = field(default=False, repr=False)

    def print(self, d: int = 0, v: bool = False):

        def is_node(n): return isinstance(n, ASTNode)
        def has_nodes(n): return isinstance(n, list) and n and is_node(n[0])

        # header
        p = '  ' * d + '|'
        # print(f'{p}-{self.__class__.__name__}')
        print(f'{p}-{self}')

        # attrs
        p, d = p + '  ', d + 1
        for k in self.__dict__:
            n = getattr(self, k)
            if has_nodes(n):
                if v: print(f'{p}{k}=(')
                for nb in getattr(self, k):
                    nb.print(d + 1)
                if v: print(f'{p})')
            elif is_node(n):
                if v: print(f'{p}{k}=(')
                n.print(d + 1)
                if v: print(f'{p})')
            else:
                if v: print(f'{p}{k}={n}')

    def gen_asm(self, ra: RegisterAllocator, *args, **kwargs) -> str:
        return '\nNotImplemented!'


@dataclass
class Root(ASTNode):
    children: list[ASTNode] = field(default_factory=list, repr=False)


@dataclass
class Expr(ASTNode): pass


@dataclass
class Stmt(ASTNode): pass


@dataclass
class Decl(ASTNode): pass


@dataclass
class NumExpr(Expr):
    val: int | None = None


@dataclass
class BinOp(Expr):
    is_leaf: bool = field(default=True, repr=False)
    op1: NumExpr | Expr | None = field(default=None, repr=False)
    op2: NumExpr | Expr | None = field(default=None, repr=False)


@dataclass
class ParenExpr(Expr):
    expr: Expr | None = field(default=None, repr=False)


@dataclass
class DeclRefExpr(Expr):
    ident: str = ''


@dataclass
class AddOp(BinOp): pass


@dataclass
class CompoundStmt(Stmt):
    stmts: list[Stmt] = field(default_factory=list, repr=False)


@dataclass
class VarDecl(Decl):
    type: ASTNode | None = None
    ident: str = ''
    val: Expr | None = field(default=None, repr=False)


@dataclass
class DeclStmt(Stmt):
    var: VarDecl = field(default_factory=VarDecl, repr=False)


@dataclass
class ReturnStmt(Stmt):
    expr: Expr | None = field(default=None, repr=False)


@dataclass
class FunctionDecl(Decl):
    rtype: ASTNode | None = None
    ident: str = ''
    args: list[VarDecl] = field(default_factory=list)
    body: CompoundStmt = field(default_factory=CompoundStmt)

    def __repr__(self):
        return f'{self.__class__.__name__}(rtype={self.rtype}, ident={self.ident})'


def gen_asm(root: ASTNode) -> str:

    res = ''

    ra = RegisterAllocator()

    # postorder traversal
    def _dig(root: ASTNode):
        nonlocal res
        if not root.is_leaf:
            for k in root.__dict__:
                x = getattr(root, k)
                if isinstance(x, list): [_dig(k) for k in x]
                if isinstance(x, ASTNode): _dig(x)
        res += root.gen_asm(ra)
        print(root)

    _dig(root)
    return res
