from typing import Callable, Union
from syntax import Exp, Stmt
from syntax import Plus, Minus, Mult, Div, Eq, Leq, Mod
import syntax


class Value:
    pass


class Unit(Value):
    def __str__(self):
        return "()"

    def __hash__(self):
        return hash(None)

    def __eq__(self, other):
        return isinstance(other, Unit)


class Num(Value):
    value: Union[int, float]

    def __init__(self, v: Union[int, float]):
        self.value = v

    def __str__(self):
        return str(self.value)

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Num) and self.value == other.value


class String(Value):
    value: str

    def __init__(self, s: str):
        self.value = s

    def __str__(self):
        return self.value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, String) and self.value == other.value


class Bool(Value):
    value: bool

    def __init__(self, b: bool):
        self.value = b

    def __str__(self):
        return str(self.value)

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Bool) and self.value == other.value


class Hashmap(Value):
    elements: dict[Value, Value]

    def __init__(self, e: dict[Value, Value]):
        self.elements = e

    def __str__(self):
        return f"{{{', '.join(f'{a}: {b}' for a, b in self.elements.items())}}}"


class Array(Value):
    elements: list[Value]

    def __init__(self, e: list[Value]):
        self.elements = e

    def __str__(self):
        return f"[{', '.join([str(e) for e in self.elements])}]"


# THE CROWN JEWEL
class Closure(Value):
    parameters: list[str]
    body: list[Stmt]
    env: list[dict[str, Value]]

    def __init__(self, p: list[str], b: list[Stmt], env: list[dict[str, Value]]):
        self.parameters = p
        self.body = b
        self.env = env

    def __str__(self):
        return "<<Closure>>"


class PrimOp(Value):
    func: Callable[[list[Value]], Value]

    def __init__(self, func):
        self.func = func

    def __str__(self):
        return "<<PrimOp>>"


class Interp:
    env_stack: list[dict[str, Value]]

    def __init__(self, env_stack: list[dict[str, Value]]):
        self.env_stack = env_stack

    def assert_num(self, v: Value) -> Union[int, float]:
        match v:
            case Num(value=value):
                return value
            case _:
                print(v, type(v))
                raise TypeError("Num")

    def assert_bool(self, v: Value) -> bool:
        match v:
            case Bool(value=value):
                return value
            case _:
                raise TypeError("Bool")

    def arith_op(self, lhs: Value, rhs: Value, f: Callable) -> Value:
        lhs = self.assert_num(lhs)
        rhs = self.assert_num(rhs)
        return f(lhs, rhs)

    def exec(self, s: Stmt) -> None:
        match s:
            case syntax.NakedExp(exp=exp):
                self.eval(exp)
            case syntax.Let(name=name, init=init):
                match init:
                    case syntax.Func():
                        init = self.eval(init)
                        self.env_stack[-1][name] = init
                        init.env[-1][name] = init
                    case _:
                        init = self.eval(init)
                        self.env_stack[-1][name] = init

            case syntax.Assign(target=target, value=value):
                match target:
                    # TODO: more expr???
                    case syntax.Variable(name=name):
                        idx = self.lookup(name)
                        value = self.eval(value)
                        self.env_stack[idx][name] = value
                    case _:
                        raise ValueError("Invalid lvalue")
            # big brain moment
            case syntax.Return(tb_returned=tb_returned):
                tb_returned = self.eval(tb_returned)
                raise Return(tb_returned)
            case _:
                raise ValueError("Unknown Statement")

    def block(self, b: list[Stmt]) -> Value:
        match b:
            case []:
                return Unit()
            case [*stuff, last]:
                ret = None
                self.env_stack.append({})

                for s in stuff:
                    self.exec(s)

                match last:
                    case syntax.NakedExp(exp=exp):
                        ret = self.eval(exp)
                    case _:
                        self.exec(last)
                        ret = Unit()

                self.env_stack.pop()
                return ret

    def eval(self, e: Exp) -> Value:
        # print(e, type(e))
        match e:
            # literals
            case syntax.Unit():
                return Unit()
            case syntax.Bool(value=value):
                return Bool(value)
            case syntax.Num(value=value):
                return Num(value)
            case syntax.String(value=value):
                return String(value)

            # thicc literals
            case syntax.Array(elements=elements):
                return Array([self.eval(e) for e in elements])
            case syntax.Hashmap(elements=elements):
                return Hashmap(
                    {self.eval(k): self.eval(v) for k, v in elements.items()}
                )

            case syntax.Variable(name=name):
                idx = self.lookup(name)
                return self.env_stack[idx][name]
            case syntax.BinOp(lhs=lhs, rhs=rhs, op=op):

                lhs = self.eval(lhs)
                rhs = self.eval(rhs)
                match op:

                    case Plus():
                        return self.arith_op(lhs, rhs, lambda x, y: Num(x + y))
                    case Minus():
                        return self.arith_op(lhs, rhs, lambda x, y: Num(x - y))
                    case Mult():
                        return self.arith_op(lhs, rhs, lambda x, y: Num(x * y))
                    case Div():
                        lhs = self.assert_num(lhs)
                        rhs = self.assert_num(rhs)
                        if rhs == 0:
                            raise DivZeroError()
                        return Num(lhs / rhs)
                    case Eq():
                        return self.arith_op(lhs, rhs, lambda x, y: Bool(x == y))
                    case Leq():
                        return self.arith_op(lhs, rhs, lambda x, y: Bool(x <= y))
                    case Mod():
                        return self.arith_op(lhs, rhs, lambda x, y: Num(x % y))
                    # ..
            case syntax.Cond(
                condition=condition, perchance=perchance, perchance_not=perchance_not
            ):
                condition = self.eval(condition)
                condition = self.assert_bool(condition)

                if condition:
                    return self.block(perchance)
                else:
                    match perchance_not:
                        case None:
                            return Unit()
                        case syntax.Cond():
                            return self.eval(perchance_not)
                        case [*stmts]:
                            return self.block(stmts)
            case syntax.Block(stmts=stmts):
                return self.block(stmts)

            case syntax.Field(tb_fielded=tb_fielded, field=field):
                tb_fielded = self.eval(tb_fielded)
                match tb_fielded:
                    case Hashmap(elements=elements):
                        return elements[String(field)]
                    case _:
                        raise TypeError("HashMap")
            case syntax.Subscript(tb_indexed=tb_indexed, index=index):
                tb_indexed = self.eval(tb_indexed)
                match tb_indexed:
                    case Hashmap(elements=elements):
                        index = self.eval(index)
                        return elements[index]
                    case Array(elements=elements):
                        index = self.eval(index)
                        match index:
                            case Num(value=int(ix)):
                                return elements[ix]
                            case _:
                                raise TypeError("Int")
                    case _:
                        raise TypeError("Subscriptable (Array / HashMap)")
            case syntax.Func(params=params, body=body):
                return Closure(params, body, [dict(env) for env in self.env_stack])
            case syntax.Call(func=func, arguments=args):
                func = self.eval(func)
                match func:
                    case Closure(parameters=params, body=body, env=e):
                        if len(args) != len(params):
                            raise IncorrectArity(len(params), len(args))
                        local = e + [
                            {name: self.eval(arg) for name, arg in zip(params, args)}
                        ]
                        try:
                            return Interp(local).block(body)
                        except Return as ret:
                            return ret.value
                    case PrimOp(func=func):
                        args = [self.eval(arg) for arg in args]
                        return func(args)

                    case _:
                        raise TypeError("Closure")

            case syntax.While(condition=condition, body=body):
                # condition = self.eval(condition)
                # condition = self.assert_bool(condition)

                while self.assert_bool(self.eval(condition)):
                    self.block(body)
                return Unit()
            case _:
                raise ValueError("Skill Issue")

    def lookup(self, name: str):
        for idx, env in list(enumerate(self.env_stack))[::-1]:
            if name in env:
                return idx

        raise UnboundVariable(name)


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


class UnboundVariable(RuntimeError):
    name: str

    def __init__(self, e: str):
        self.name = e


class Return(Exception):
    value: Value

    def __init__(self, v: Value):
        self.value = v


def make_global_env() -> dict[str, Value]:
    def puts(params: list[Value]) -> Value:
        print(*[str(val) for val in params], sep="\n")

    def length(params: list[Value]) -> Value:
        match params:
            case [e]:
                match e:
                    case String(value=v) | Hashmap(elements=v) | Array(elements=v):
                        return len(v)
                    case _:
                        raise TypeError("String/Hashmap/Array")
            case _:
                raise IncorrectArity(1, len(params))

    return {"puts": PrimOp(puts), "len": PrimOp(length)}
