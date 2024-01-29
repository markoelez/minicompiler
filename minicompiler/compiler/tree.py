from dataclasses import dataclass, field


class RegisterAllocator:
    def __init__(self):
        self.regs = {f'X{i}' for i in range(31)}
        self.h = {}

    def get_free(self) -> str:
        return self.regs.pop()

    def alloc_var(self, var: str) -> str:
        reg = self.get_free()
        self.h[var] = reg
        return reg

    def get_reg(self, var: str) -> str:
        return self.h.get(var, 'NA')


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

    def gen_asm(self, ra: RegisterAllocator, *args, **kwargs) -> list[str]:
        return [f'{self.__class__.__name__} -- NA']


@dataclass
class Root(ASTNode):
    children: list[ASTNode] = field(default_factory=list, repr=False)

    def gen_asm(self, ra: RegisterAllocator, *args, **kwargs) -> list[str]:
        a = []
        for x in self.children:
            a += x.gen_asm(ra)
        return a


@dataclass
class Expr(ASTNode):
    # outputs
    out_reg: str | None = field(default=None, repr=False)


@dataclass
class Stmt(ASTNode): pass


@dataclass
class Decl(ASTNode): pass


@dataclass
class NumExpr(Expr):
    # inputs
    val: int | None = None
    # outputs
    out_reg: str | None = field(default=None, repr=False)

    def gen_asm(self, ra: RegisterAllocator, *args, **kwargs) -> list[str]:
        self.out_reg = ra.get_free()
        return [f'MOV {self.out_reg}, #{self.val}']


@dataclass
class BinOp(Expr):
    is_leaf: bool = field(default=True, repr=False)
    op1: Expr = field(default_factory=Expr, repr=False)
    op2: Expr = field(default_factory=Expr, repr=False)


@dataclass
class ParenExpr(Expr):
    expr: Expr | None = field(default=None, repr=False)


@dataclass
class DeclRefExpr(Expr):
    # inputs
    ident: str = ''
    # outputs
    out_reg: str = field(default='NA', repr=False)

    def gen_asm(self, ra: RegisterAllocator, *args, **kwargs) -> list[str]:
        self.out_reg = ra.get_reg(self.ident)
        return []


@dataclass
class AddOp(BinOp):
    # outputs
    out_reg: str | None = field(default=None, repr=False)

    def gen_asm(self, ra: RegisterAllocator, *args, **kwargs) -> list[str]:

        op1, op2 = self.op1, self.op2

        asm1, asm2 = op1.gen_asm(ra), op2.gen_asm(ra)

        r1, r2 = op1.out_reg, op2.out_reg

        self.out_reg = ra.get_free()

        a = []
        a += asm1
        a += asm2
        a += [f'ADD {self.out_reg}, {r1}, {r2}']
        return a


@dataclass
class CompoundStmt(Stmt):
    stmts: list[Stmt] = field(default_factory=list, repr=False)

    def gen_asm(self, ra: RegisterAllocator, *args, **kwargs) -> list[str]:
        a = []
        for x in self.stmts:
            a += x.gen_asm(ra)
        return a


@dataclass
class VarDecl(Decl):
    type: ASTNode | None = None
    ident: str = ''
    val: Expr = field(default_factory=Expr, repr=False)

    def gen_asm(self, ra: RegisterAllocator, *args, **kwargs) -> list[str]:

        # assign register to variable
        reg = ra.alloc_var(self.ident)

        # codegen for associated value expression
        asm = self.val.gen_asm(ra)

        # output register for assigned expression
        val = self.val.out_reg

        a: list[str] = []
        a += asm
        a += [f'MOV {reg}, {val}']
        return a


@dataclass
class DeclStmt(Stmt):
    var: VarDecl = field(default_factory=VarDecl, repr=False)

    def gen_asm(self, ra: RegisterAllocator, *args, **kwargs) -> list[str]:
        return self.var.gen_asm(ra)


@dataclass
class ReturnStmt(Stmt):
    # inputs
    expr: Expr = field(default_factory=Expr, repr=False)
    # outputs
    out_reg: str = field(default='X0', repr=False)  # always place output in X0

    def gen_asm(self, ra: RegisterAllocator, *args, **kwargs) -> list[str]:

        expr = self.expr.gen_asm(ra)

        in_reg = self.expr.out_reg

        a = []
        a += expr
        a += [f'MOV {self.out_reg}, {in_reg}']
        a += ['RET']
        return a


@dataclass
class FunctionDecl(Decl):
    rtype: ASTNode | None = None
    ident: str = ''
    args: list[VarDecl] = field(default_factory=list)
    body: CompoundStmt = field(default_factory=CompoundStmt)

    def gen_asm(self, ra: RegisterAllocator, *args, **kwargs) -> list[str]:
        body = self.body.gen_asm(ra)

        a = []
        a += [f'.global {self.ident}']
        a += [f'{self.ident}:']
        a += body
        return a

    def __repr__(self):
        return f'{self.__class__.__name__}(rtype={self.rtype}, ident={self.ident})'


def gen_asm(root: ASTNode) -> str:
    ra = RegisterAllocator()
    a = root.gen_asm(ra)
    return '\n'.join(a)
