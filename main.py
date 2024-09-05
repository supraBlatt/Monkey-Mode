from sys import argv 
from parser import parser, Parser
from eval import Interp


def main():
    filename = argv[1]
    src = open(filename, 'r').read()

    #text = '{"key": ["item0", "item1", 3.14]}'
    parsed = parser.parse(src)
    #print(parsed.pretty())
    parsed = Parser().transform(parsed)
    #print(*parsed, sep="\n")

    interp = Interp({})
    interp.block(parsed)

if __name__ == '__main__':
    main()

