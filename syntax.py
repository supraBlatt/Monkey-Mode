from __future__ import annotations 
from typing import Optional, Union

class Exp:
    pass

class Operator:
    pass 

class Stmt:
    pass 

class Block(Exp):
    stmts:  list[Stmt]

    def __init__(self, s: list[Stmt]):
        self.stmts = s 

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
        return self.value

class Bool(Exp):
    value: bool
    
    def __init__(self, b: bool):
        self.value = b

    def __str__(self):
        return str(self.value)
    
class BinOp(Exp):
    lhs: Exp
    rhs : Exp 
    op: Operator

    def __init__(self, l: Exp, r: Exp, o: Operator):
        self.rhs = r 
        self.lhs = l 
        self.op  = o 

# f (x)
class Call(Exp):
    func: Exp
    arguments: list[Exp]

    def __init__(self, f: Exp, a: list[Exp]):
        self.func = f
        self.arguments = a 

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

class Field(Exp):
    tb_fielded: Exp 
    field: str 

    def __init__(self, tb: Exp, f: str):
        self.tb_fielded = tb 
        self.field = f

class Array(Exp):
    elements: list[Exp]

    def __init__(self, e: list[Exp]):
        self.elements = e

class Subscript(Exp):
    tb_indexed: Exp 
    index: Exp

    def __init__(self, tb: Exp, i: Exp):
        self.tb_indexed = tb 
        self.index = i

class Unit(Exp):
    def __str__(self):
        return "()"

class Func(Exp):
    params: list[str]
    body: list[Stmt]

    def __init__(self, p: list[str], b: list[Stmt]):
        self.params = p
        self.body = b 

class Cond(Exp):
    condition: Exp 
    perchance: Block
    perchance_not: Union[None, Cond, Block]

    def __init__(self, c: Exp, p: Block, pn: Union[None, Cond, Block]):
        self.condition = c 
        self.perchance = p 
        self.perchance_not = pn

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
    pass 
class Minus(Operator):
    pass 
class Mult(Operator):
    pass 
class Div(Operator):
    pass 
class Eq(Operator):
    pass
class Leq(Operator):
    pass
