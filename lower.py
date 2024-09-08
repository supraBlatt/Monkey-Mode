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
                s = Let(name, self.lower(init))
                self.stmts.append(s)
            case Assign(target=target, value=value):
                #??
                pass 

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

    def make_variable(self) -> str:
        name = f"${self.timestamp}"
        self.timestamp += 1
        return name
