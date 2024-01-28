import random
from dataclasses import dataclass, field
from typing import Any
from abc import abstractmethod


class RegisterAllocator:
    def __init__(self):
        self.regs = {f'X{i}' for i in range(31)}

    def get_free(self) -> str:
        return self.regs.pop()


@dataclass
class ASTNode:

    is_leaf: bool = False

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

    @abstractmethod
    def gen_asm(self, ra: RegisterAllocator, *args, **kwargs) -> str:
        raise NotImplementedError()


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
    is_leaf: bool = True
    op1: NUMBER | EXPR | None = None
    op2: NUMBER | EXPR | None = None


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
