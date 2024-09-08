from syntax import Exp, Stmt
import syntax


class PreRuntimeError(Exception):
    pass


class UnboundVariable(PreRuntimeError):
    name: str

    def __init__(self, e: str):
        self.name = e


class RValueAssignment(PreRuntimeError):
    pass


class Anal:
    env_stack: list[set[str]]

    def __init__(self, env_stack: list[set[str]]):
        self.env_stack = env_stack

    def stmt(self, s: Stmt) -> None:
        match s:
            case syntax.NakedExp(exp=exp):
                self.analyse(exp)
            case syntax.Let(name=name, init=init):
                match init:
                    case syntax.Func():
                        self.env_stack[-1].add(name)
                        self.analyse(init)
                    case _:
                        self.analyse(init)
                        self.env_stack[-1].add(name)
                    
            case syntax.Assign(target=target, value=value):
                match target:
                    case syntax.Variable():
                        self.analyse(target)
                        self.analyse(value)
                    case _:
                        raise RValueAssignment()
            case syntax.Return(tb_returned=tb_returned):
                self.analyse(tb_returned)
            case _:
                raise ValueError("Uknown Statement")

    def block(self, b: list[Stmt]) -> None:
        match b:
            case []:
                return
            case [*stuff]:
                self.env_stack.append(set())
                for s in stuff:
                    self.stmt(s)
                self.env_stack.pop()

    def analyse(self, e: Exp) -> None:
        match e:
            case syntax.Unit():
                return
            case syntax.Bool(value=value):
                return
            case syntax.Num(value=value):
                return
            case syntax.String(value=value):
                return

            # compounds
            case syntax.Array(elements=elements):
                for e in elements:
                    self.analyse(e)
            case syntax.Hashmap(elements=elements):
                for k, v in elements.items():
                    self.eval(k)
                    self.eval(v)

            case syntax.Variable(name=name):
                self.lookup(name)
            case syntax.BinOp(lhs=lhs, rhs=rhs, op=op):

                lhs = self.analyse(lhs)
                rhs = self.analyse(rhs)

            case syntax.Cond(
                condition=condition, perchance=perchance, perchance_not=perchance_not
            ):
                self.analyse(condition)
                self.block(perchance)
                match perchance_not:
                    case None:
                        return
                    case syntax.Cond():
                        self.analyse(perchance_not)
                    case [*stmts]:
                        self.block(stmts)

            case syntax.Block(stmts=stmts):
                self.block(stmts)

            case syntax.Field(tb_fielded=tb_fielded, field=field):
                self.analyse(tb_fielded)
                self.analyse(field)
            case syntax.Subscript(tb_indexed=tb_indexed, index=index):
                self.analyse(tb_indexed)
                self.analyse(index)

            case syntax.Func(params=params, body=body):
                self.env_stack.append(params)
                self.block(body)
                self.env_stack.pop()

            case syntax.Call(func=func, arguments=args):
                self.analyse(func)
                for arg in args:
                    self.analyse(arg)
            case syntax.While(condition=condition, body=body):
                self.analyse(condition)
                self.block(body)
            case _:
                raise ValueError("Skull Emoji")

    def lookup(self, name: str):
        for env in self.env_stack[::-1]:
            if name in env:
                return

        raise UnboundVariable(name)


def make_global_env() -> set[str]:
    return ["puts", "len"]
