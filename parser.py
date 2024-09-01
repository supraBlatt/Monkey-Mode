from lark import Lark, Transformer
from syntax import *

parser = Lark(r"""
    block : stmt*          
    
    ?stmt : expr ";"                -> naked
          | "let" id "=" expr ";"   -> let
          | "return" expr ";"       -> ret

    ?expr : atom
               
    ?atom : "()"                                        -> unit 
          | SIGNED_NUMBER                               -> number
          | "true"                                      -> true 
          | "false"                                     -> false 
          | id                                          -> var
          | ESCAPED_STRING                              -> string
          | "fn" "(" [id ("," id)*]  ")" "{" block "}"  -> func

              
    id : /[a-zA-Z][a-zA-Z0-9_]*/
    

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS

    """, start='block', debug=True, strict=True, parser="lalr")

class Parser(Transformer):
    def unit(self, _):
        return Unit() 
    
    def number(self, n):
        (n,) = n 
        if "." in n:
            return Num(float(n))
        return Num(int(n))
    
    def true(self, _):
        return Bool(True)
    
    def false(self, _):
        return Bool(False)
    
    def string(self, s):
        (s,) = s
        return String(s)
    
    def  block(self, b):
        return list(b)

    def naked(self, e):
        (e,) = e 
        return NakedExp(e)

    def id(self, items):
        (id, ) = items 
        return str(id)

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
        print(items)
