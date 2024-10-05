from __future__ import annotations
from typing import Optional, Union


class Exp:
    pass


class Operator:
    pass


class Stmt:
    pass


class Block(Exp):
    stmts: list[Stmt]

    def __init__(self, s: list[Stmt]):
        self.stmts = s
    
    def __str__(self):
        return f"{{{' '.join([str(e) for e in self.stmts])}}}"


class Num(Exp):
    value: Union[int, float]

    def __init__(self, v: Union[int, float]):
        self.value = v

    def __str__(self):
        return str(self.value)


class String(Exp):
    value: str

    def __init__(self, s: str):
        self.value = s

    def __str__(self):
        return f'"{self.value}"'


class Bool(Exp):
    value: bool

    def __init__(self, b: bool):
        self.value = b

    def __str__(self):
        return str(self.value)


class BinOp(Exp):
    lhs: Exp
    rhs: Exp
    op: Operator

    def __init__(self, l: Exp, r: Exp, o: Operator):
        self.rhs = r
        self.lhs = l
        self.op = o

    def __str__(self):
        return f"({self.lhs} {self.op} {self.rhs})"


class Call(Exp):
    func: Exp
    arguments: list[Exp]

    def __init__(self, f: Exp, a: list[Exp]):
        self.func = f
        self.arguments = a

    def __str__(self):
        return f"{self.func}({','.join([str(x) for x in self.arguments])})"


class Variable(Exp):
    name: str

    def __init__(self, n: str):
        self.name = n

    def __str__(self):
        return self.name


class Hashmap(Exp):
    elements: dict[Exp, Exp]

    def __init__(self, e: dict[Exp, Exp]):
        self.elements = e

    def __str__(self):
        return f"{{{', '.join(f'{a}: {b}' for a, b in self.elements.items())}}}"


class Field(Exp):
    tb_fielded: Exp
    field: str

    def __init__(self, tb: Exp, f: str):
        self.tb_fielded = tb
        self.field = f

    def __str__(self):
        return f"{str(self.tb_fielded)}.{self.field}"


class Array(Exp):
    elements: list[Exp]

    def __init__(self, e: list[Exp]):
        self.elements = e

    def __str__(self):
        return f"[{', '.join([str(e) for e in self.elements])}]"


class Subscript(Exp):
    tb_indexed: Exp
    index: Exp

    def __init__(self, tb: Exp, i: Exp):
        self.tb_indexed = tb
        self.index = i

    def __str__(self):
        return f"{self.tb_indexed}[{self.index}]"


class Unit(Exp):
    def __str__(self):
        return "()"


class Func(Exp):
    params: list[str]
    body: list[Stmt]

    def __init__(self, p: list[str], b: list[Stmt]):
        self.params = p
        self.body = b

    def __str__(self):
        return (
            f"fn({','.join(self.params)}) {{{''.join([str(s) for s in self.body])}}}"
        )


class Cond(Exp):
    condition: Exp
    perchance: list[Stmt]
    perchance_not: Union[None, Cond, list[Stmt]]

    def __init__(self, c: Exp, p: list[Stmt], pn: Union[None, Cond, list[Stmt]]):
        self.condition = c
        self.perchance = p
        self.perchance_not = pn

    def __str__(self):
        tmp = None
        match self.perchance_not:
            case [*s]:
                tmp = " else " + block_string(s)
            case Cond():
                tmp = " else " + str(self.perchance_not)
            case None:
                tmp = ""

        return f"if ({self.condition}) {block_string(self.perchance)}{tmp}"


class While(Exp):
    condition: Exp
    body: list[Stmt]

    def __init__(self, condition: Exp, body: list[Stmt]):
        self.condition = condition
        self.body = body

    def __str__(self):
        return f"while ({self.condition}) {block_string(self.body)}"


def block_string(s: list[Stmt]) -> str:
    #print("list: ", s, type(s))
    tmp = "\n\t".join([str(x) for x in s])
    return f"{{\n\t{tmp}\n}}"


class NakedExp(Stmt):
    exp: Exp

    def __init__(self, e: Exp):
        self.exp = e

    def __str__(self):
        return str(self.exp) + ";"


class Let(Stmt):
    name: str
    init: Exp

    def __init__(self, n: str, i: Exp):
        self.name = n
        self.init = i

    def __str__(self):
        return f"let {self.name} = {self.init};"


class Return(Stmt):
    tb_returned: Exp

    def __init__(self, tb: Exp):
        self.tb_returned = tb

    def __str__(self):
        return f"return {self.tb_returned};"


class Assign(Stmt):
    target: Exp
    value: Exp

    def __init__(self, t: Exp, v: Exp):
        self.target = t
        self.value = v

    def __str__(self):
        return f"{self.target} = {self.value};"


class Plus(Operator):
    def __str__(self):
        return "+"


class Minus(Operator):
    pass


class Mult(Operator):
    pass


class Div(Operator):
    pass


class Eq(Operator):
    def __str__(self):
        return "=="


class Leq(Operator):
    def __str__(self):
        return "<="


class Mod(Operator):
    pass
