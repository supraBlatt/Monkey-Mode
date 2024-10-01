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
                exp = self.lower(exp)
            case Let(name=name, init=init):
                stmt = Let(name, self.lower(init))
                self.stmts.append(stmt)
            case Assign(target=target, value=value):
                match target:
                    case Subscript(tb_indexed=tb_indexed, index=index):
                        tb_indexed = self.lower(tb_indexed)
                        index = self.lower(index)
                        value = self.lower(value)
                        stmt = Assign(Subscript(tb_indexed, index), value)
                        self.stmts.append(stmt)
                    case Field(tb_fielded=tb_fielded, field=field):
                        tb_fielded = self.lower(tb_fielded)
                        value = self.lower(value)
                        stmt = Assign(Subscript(tb_fielded, String(field)), value)
                        self.stmts.append(stmt)
                    case Variable(name=name):
                        value = self.lower(value)
                        stmt = Assign(target, value)
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
            case Subscript(tb_indexed=tb_indexed, index=index):
                tb_indexed = self.lower(tb_indexed)
                index = self.lower(index)
                exp = Subscript(tb_indexed, index)
                name = self.make_variable()
                self.stmts.append(Let(name, exp))
                return Variable(name)
            case Field(tb_fielded=tb_fielded, field=field):
                tb_fielded = self.lower(tb_fielded)
                field = String(field)
                exp = Subscript(tb_fielded, field)
                name = self.make_variable()
                self.stmts.append(Let(name, exp))
                return Variable(name)
            case Array(elements=elements):
                elements = [self.lower(e) for e in elements]
                exp = Array(elements)
                name = self.make_variable()
                self.stmts.append(Let(name, exp))
                return Variable(name)
            case Hashmap(elements=elements):
                elements = {self.lower(k) : self.lower(v) for k,v in elements.items()}
                name = self.make_variable()
                exp = Hashmap(elements)
                self.stmts.append(Let(name, exp))
                return Variable(name)
            case Cond(condition=condition, perchance=perchance, perchance_not=perchance_not):
                condition = self.lower(condition)

                # handle perchance like Func 
                ir = IR_Transformer()
                atom = ir.lower_block(perchance)
                match atom:
                    case Unit():
                        pass 
                    case _:
                        

                match perchance_not:
                    case None:
                        pass 
                    case Cond():
                        perchance_not = self.lower(perchance_not)
                    case [*stmts]:
                        perchance_not = self.lower_block(stmts)
                exp = Cond(condition, perchance, perchance_not)
                name = self.make_variable()
                self.stmts.append(Let(name, exp))
                return Variable(name)
            case While(condition=condition, body=body):
                condition = self.lower(condition)
                body = self.lower_block(body)
                exp = While(condition, body)
                name = self.make_variable()
                self.stmts.append(Let(name, exp))
                return Variable(name)
            case _:
                print(x, type(x))
                raise ValueError("Get Ratioed")

    def make_variable(self) -> str:
        name = f"${self.timestamp}"
        self.timestamp += 1
        return name
