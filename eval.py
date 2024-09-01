from typing import Optional, Union
from syntax import Exp, Stmt
import syntax 

from syntax import Plus, Minus, Mult, Div, Eq, Leq

class Value:

    pass

class Unit(Value):
    pass

class Num(Value):
    value: Union[int, float]
    
    def __init__(self, v: Union[int, float]):
        self.value = v

class String(Value):
    value: str
    
    def __init__(self, s: str):
        self.value = s

class Bool(Value):
    value: bool
    
    def __init__(self, b: bool):
        self.value = b

class Hashmap(Value):
    elements: dict[Value, Value]

    def __init__(self, e: dict[Value, Value]):
        self.elements = e 

class Array(Value):
    elements: list[Value]

    def __init__(self, e: list[Value]):
        self.elements = e

# THE CROWN JEWEL
class Closure(Value):
    parameters: list[str]
    body: list[Stmt]

    def __init__(self, p: list[str], b: list[Stmt]):
        self.parameters = p 
        self.body = b 

class Interp:
    env: dict[str, Value]

    def __init__(self, e: dict[str, Value]):
        self.env = e
    
    def assert_num(v: Value) -> Union[int, float]:
        match v:
            case Num(value):
                return value 
            case _: 
                raise TypeError("Num")

    def assert_bool(v: Value) -> bool:
        match v: 
            case Bool(value):
                return value 
            case _:
                raise TypeError("Bool")

    def arith_op(self, lhs: Value, rhs: Value, f: function) -> Value:
        lhs = self.assert_num(lhs)
        rhs = self.assert_num(rhs)
        return f(lhs, rhs)
    
    def exec(self, s: Stmt) -> None:
        match s:
            case syntax.NakedExp(exp):
                self.eval(exp);
            case syntax.Let(name, init):
                init = self.eval(init)
                self.env[name] = init
            case syntax.Assign(target, value):
                match target:
                    # TODO: more expr???
                    case syntax.Variable(name):
                        value = self.eval(value)
                        self.env[name] = value 
            # big brain moment
            case syntax.Return(tb_returned):
                tb_returned = self.eval(tb_returned)
                raise Return(tb_returned)

    def block(self, b: list[Stmt]) -> Value:
        match b: 
            case []:
                return Unit()
            case [*stuff, last]:
                for s in stuff:
                    self.exec(s)
                match last:
                    case syntax.NakedExp(exp):
                        return self.eval(exp)
                    case _:
                        return Unit() 
        
    def eval(self, e: Exp) -> Value:
        match e: 
            # literals
            case syntax.Unit():
                return Unit()
            case syntax.Bool(value):
                return Bool(value)
            case syntax.Num(value):
                return Num(value)
            case syntax.String(value):
                return String(value)
            
            # thicc literals
            case syntax.Array(elements):
                return Array([self.eval(e) for e in elements])
            case syntax.Hashmap(elements):
                return Hashmap({self.eval(e1): self.eval(e2) for e1, e2 in elements.items()})
            
            case syntax.Variable(name):
                return self.env[name]
            case syntax.BinOp(lhs, rhs, op):

                lhs = self.eval(lhs)
                rhs = self.eval(rhs)
                match op: 

                    case Plus():
                        return self.arith_op(lhs, rhs, lambda x,y: Num(x + y))
                    case Minus():
                        return self.arith_op(lhs, rhs, lambda x,y: Num(x - y))
                    case Mult():
                        return self.arith_op(lhs, rhs, lambda x,y: Num(x * y))
                    case Div():
                        lhs = self.assert_num(lhs)
                        rhs = self.assert_num(rhs)
                        if (rhs == 0): raise DivZeroError()
                        return Num(lhs / rhs)
                    case Eq():
                        return self.arith_op(lhs, rhs, lambda x,y: Bool(x == y))
                    case Leq():
                        return self.arith_op(lhs, rhs, lambda x,y: Bool(x <= y))
                    #.. 
            case syntax.Cond(condition, perchance, perchance_not):
                condition = self.eval(condition)
                condition = self.assert_bool(condition)

                if condition:
                    return self.block(perchance)
                else: 
                    match perchance_not:
                        case None:
                            return Unit()
                        case wildcard:
                            return self.eval(wildcard)
            case syntax.Block(stmts):
                return self.block(stmts)
            
            case syntax.Field(tb_fielded, field):
                tb_fielded = self.eval(tb_fielded)
                match tb_fielded:
                    case Hashmap(elements):
                        return elements[String(field)]
                    case _:
                        raise TypeError("HashMap")
            case syntax.Subscript(tb_indexed, index):
                tb_indexed = self.eval(tb_indexed)
                match tb_indexed:
                    case Hashmap(elements):
                        index = self.eval(index)
                        return elements[index]
                    case Array(elements):
                        index = self.eval(index)
                        match index:
                            case Num(value=int(ix)):
                                return elements[ix]
                            case _:
                                raise TypeError("Int")
                    case _:
                        raise TypeError("Subscriptable (Array / HashMap)")
            case syntax.Func(params, body):
                return Closure(params, body)
            case syntax.Call(func, args):
                func = self.eval(func)
                match func:
                    case Closure(params, body):
                        if len(args) != len(params): raise IncorrectArity(len(params), len(args))
                        env = {name: self.eval(arg) for name, arg in zip(params, args)}
                        try:
                            return Interp(env).block(body)
                        except Return as ret:
                            return ret.value

                    case _:
                        raise TypeError("Closure")

                  
class RuntimeError(Exception):
    pass

class TypeError(RuntimeError):
    expected: str 

    def __init__(self, e: str):
        self.expected = e 
    
class DivZeroError(RuntimeError):
    pass 

class IncorrectArity(RuntimeError):
    expected: int 
    actual: int

    def __init__(self, e: int, a: int):
        self.expected = e 
        self.actual = a

class Return(Exception):
    value: Value 

    def __init__(self, v: Value):
        self.value = v

        