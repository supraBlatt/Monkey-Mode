from lark import Lark, Transformer
from syntax import *

parser = Lark(r"""
    block : stmt*          
    
    stmt : expr ";"                                     -> naked
         | "let" ID "=" expr ";"                        -> let
         |  ID "=" expr ";"                             -> assign
         | "return" expr ";"                            -> ret

    ?expr : prec3
    
    ?prec3 : prec4
           | prec3 "<=" atom                            -> leq 
           | prec3 "==" atom                            -> eq
              
    ?prec4 : prec5
           | prec4 "+" atom                             -> plus
           | prec4 "-" atom                             -> minus
              
    ?prec5 : prec10 
           | prec5 "*" atom                             -> mult
           | prec5 "/" atom                             -> div
              
    ?prec10 : atom
            | prec10 "(" expr_list ")"                  -> like
            | prec10 "." ID                             -> comment
            | prec10 "[" expr "]"                       -> subscribe
               
    ?atom : "()"                                        -> unit 
          | SIGNED_NUMBER                               -> number
          | "true"                                      -> true 
          | "false"                                     -> false 
          | ID                                          -> var
          | ESCAPED_STRING                              -> string
          | "fn" "(" [ID ("," ID)*]  ")" "{" block "}"  -> func
          | "[" expr_list "]"                           -> array
          | "{" [pair ("," pair)*] "}"                  -> hash
          | perchance                                   -> perhaps 

    ?perchance: "if" "(" expr ")" "{" block "}" ["else" perchance_not]
    ?perchance_not: perchance | "{" block "}"

    ?pair: (expr ":" expr)
    expr_list: [expr ("," expr)*]
    ID : /[a-zA-Z][a-zA-Z0-9_]*/

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS

    """, start='block', debug=True, strict=True, parser="lalr")

def binOP(op):
    return lambda _, args: BinOp(*args, op)

class Parser(Transformer):

    unit = lambda self, _: Unit()
    true = lambda self, _: Bool(True)
    false = lambda self, _: Bool(False) 

    block = list
    pair = tuple

    hash = lambda self, items: Hashmap(dict(items))
    def array(self, items):
        (items, ) = items 
        return Array(items)
    
    def expr_list(self, items):
        if items == [None]:
            return []
        return list(items)

    def number(self, n):
        (n,) = n 
        if "." in n:
            return Num(float(n))
        return Num(int(n))
    
    def string(self, s):
        (s,) = s
        return String(s)

    def naked(self, e):
        (e,) = e 
        return NakedExp(e)
    
    def let(self, items):
        id, init = items
        return Let(id, init)
    
    def ret(self, e):
        (e, ) = e
        return Return(e)
    
    def assign(self, items):
        target, value = items
        return Assign(target, value)
    
    def var(self, id):
        (id,) = id
        id = str(id)
        return Variable(id)
    
    def func(self, items):
        *args, block = items
        if args == [None]:
            args = []
        return Func(args, block)
    
    def field(self, items):
        struct, field = items
        return Field(struct, field)

    def perchance(self, items):
        condition, perchance, perchance_not = items
        return Cond(condition, perchance, perchance_not)

    def perhaps(self, items):
        (items, ) = items 
        return items
    
    # call
    def like(self, items):
        func, args = items 
        if args is None: args = [] 
        return Call(func, args)
    
    def comment(self, items):
        tb, field = items
        return Field(tb, field)
    
    def subscribe(self, items):
        tb, index = items
        return Subscript(tb, index)
    
    mult = binOP(Mult())
    plus = binOP(Plus())
    div = binOP(Div())
    minus = binOP(Minus())
    leq = binOP(Leq())
    eq = binOP(Eq())