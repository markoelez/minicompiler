from dataclasses import dataclass, field
from typing import Any


@dataclass
class ASTNode:
    def print(self, d: int = 0):

        def is_node(n): return isinstance(n, ASTNode)
        def has_nodes(n): return isinstance(n, list) and n and is_node(n[0])

        # header
        p = '  ' * d
        print(f'{p}<{self.__class__.__name__}>')

        # attrs
        p, d = p + '  ', d + 1
        for k in self.__dict__:
            n = getattr(self, k)
            if has_nodes(n):
                print(f'{p}{k}=(')
                for nb in getattr(self, k):
                    nb.print(d + 1)
                print(f'{p})')
            elif is_node(n):
                print(f'{p}{k}=(')
                n.print(d + 1)
                print(f'{p})')
            else:
                print(f'{p}{k}={n}')


@dataclass
class ROOT(ASTNode):
    children: list[ASTNode] = field(default_factory=list)


# *************** expressions ***************
@dataclass
class EXPR(ASTNode):
    pass


@dataclass
class NUMBER(EXPR):
    val: int | None = None


@dataclass
class ADDITION(EXPR):
    ops: list[NUMBER] = field(default_factory=list)


# *************** statements ***************
@dataclass
class RETURN(ASTNode):
    expr: EXPR | None = None


# *************** declarations ***************
@dataclass
class DECL(ASTNode):
    pass


@dataclass
class VAR(DECL):
    type: ASTNode | None = None
    ident: str = ''
    val: Any = None


@dataclass
class FUNC(DECL):
    rtype: ASTNode | None = None
    ident: str = ''
    args: list[VAR] = field(default_factory=list)
    body: list[ASTNode] = field(default_factory=list)
