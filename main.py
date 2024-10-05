from sys import argv
from parser import parser, Parser

import eval, static
from eval import Interp
from static import Anal

from lower import IR_Transformer

def main():
    filename = argv[1]
    src = open(filename, "r").read()

    ast = parser.parse(src)
    #print(ast.pretty())
    ast = Parser().transform(ast)
    #print(*ast, sep="\n")
    analyser = Anal([static.make_global_env()])
    analyser.block(ast)
    
    ir = IR_Transformer()
    ir.lower_block(ast)
    print(*[str(s) for s in ir.stmts], sep='\n')

    #interp = Interp([eval.make_global_env()])
    #interp.block(parsed)


if __name__ == "__main__":
    main()
