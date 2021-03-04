# Badita Rares
import sys
from os import path
import exprAnalysis as ea
import automaton as auto

argc = len(sys.argv)
input = open(sys.argv[1], "r")
output1 = open(sys.argv[2], "w")
output2 = open(sys.argv[3], "w")

runArguments = [False, False]
if argc >= 5 and sys.argv[4].lower() == 't':
    runArguments[0] = True
if argc == 6 and sys.argv[5].lower() == 't':
    runArguments[1] = True

# reading expression
expr = input.read()
syntaxTree = ea.parse(expr, runArguments[1])
nfa = auto.NFA.convert(syntaxTree)
# write nfa
output1.write(nfa.toText())
output1.close()
dfa = auto.DFA.convert(nfa)
# write dfa
output2.write(dfa.toText())
output2.close()

if runArguments[0] == True:
    dir = 'graphs'
    syntaxTree.graphViz()
    nfa.toGraphViz().render(path.join(dir, 'nfa'), view=True)
    dfa.toGraphViz().render(path.join(dir, 'dfa'), view=True)