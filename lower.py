from syntax import *


class IR_Transformer:
    stmts: list[Stmt]
    timestamp: int

    def __init__(self):
        self.stmts = []
        self.timestamp = 0

    def lower_statement(self, s: Stmt) -> None:
        match s:
            case NakedExp(exp=exp):
                self.stmts.append(self.lower(exp))
            case Let(name=name, init=init):
                stmt = Let(name, self.lower(init))
                self.stmts.append(stmt)
            case Assign(target=target, value=value):
                match target:
                    case Variable(name=name):
                        stmt = Assign(target, self.lower(value))
                        self.stmts.append(stmt)
                    case _:
                        raise ValueError("Invalid lvalue")
            case Return(tb_returned=tb_returned):
                stmt = Return(self.lower(tb_returned))
                self.stmts.append(stmt)

    def lower_block(self, b: list[Stmt]) -> Exp:
        match b:
            case []:
                return Unit()
            case [*stuff, last]:
                ret = None
                for s in stuff:
                    self.lower_statement(s)

                match last:
                    case NakedExp(exp=exp):
                        ret = self.lower(exp)
                    case _:
                        self.lower_statement(last)
                        ret = Unit()
                return ret

    def lower(self, x: Exp) -> Exp:
        match x:
            case Variable() | Num() | String() | Bool() | Unit():
                return x
            case BinOp(lhs=lhs, rhs=rhs, op=op):
                lhs = self.lower(lhs)
                rhs = self.lower(rhs)
                name = self.make_variable()
                self.stmts.append(Let(name, BinOp(lhs, rhs, op)))
                return Variable(name)
            case Block(stmts=stmts):
                return self.lower_block(stmts)
            case Func(params=params, body=body):
                ir = IR_Transformer()
                atom = ir.lower_block(body)
                match atom:
                    case Unit():
                        pass
                    case _:
                        ir.stmts.append(Return(atom))
                name = self.make_variable()
                self.stmts.append(Let(name, Func(params, ir.stmts)))
                return Variable(name)
            case Call(func=func, arguments=args):
                func = self.lower(func)
                args = [self.lower(arg) for arg in args]
                name = self.make_variable()
                self.stmts.append(Let(name, Call(func, args)))
                return Variable(name) 

            case _:
                raise ValueError("Skibidi")

    def make_variable(self) -> str:
        name = f"${self.timestamp}"
        self.timestamp += 1
        return name
