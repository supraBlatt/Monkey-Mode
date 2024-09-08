from sys import argv
from parser import parser, Parser

import eval, static
from eval import Interp
from static import Anal


def main():
    filename = argv[1]
    src = open(filename, "r").read()

    parsed = parser.parse(src)
    # print(parsed.pretty())
    parsed = Parser().transform(parsed)
    # print(*parsed, sep="\n")

    analyser = Anal([static.make_global_env()])
    analyser.block(parsed)

    #interp = Interp([eval.make_global_env()])
    #interp.block(parsed)


if __name__ == "__main__":
    main()
