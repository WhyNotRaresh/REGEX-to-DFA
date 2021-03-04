from enum import Enum as enumerator
from graphviz import Digraph
from typing import List

"""
Create abstract syntax tree for given regex by calling parse(regex)
View tree with graphviz by calling graphViz(tree)
"""

class TokenType(enumerator):
    T_LETTER = 0    # letter
    T_CON = 1       # concatenation
    T_REUN = 2      # reunion
    T_KLEENE = 3    # kleene star
    T_LPAR = 4      # left parenthesis
    T_RPAR = 5      # right parenthesis

# tree node class
class Node:
    def __init__(self, tokenType: TokenType, value: str):
        self.tokentype = tokenType
        self.value = value
        self.children = []

    # visualize graph
    def graphViz(self) -> Digraph:
        dot = Digraph(comment='abstract syntax tree for given expression')
    
        def DFS(node, index, dot):
            currentIndex = index
            dot.node(str(currentIndex), node.value)

            for child in node.children:
                index += 1
                dot.edge(str(currentIndex), str(index))
                index = DFS(child, index, dot)

            return index

        DFS(self, 0, dot)
        dot.render('graphs\\syntax-tree', view=True)
        return dot

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<' + self.value + '>'

# parse regex
def parse(inString: str, simple: bool) -> Node:
    # converting string regex into list of nodes for the parse tree
    def expressionAnalysis(s: str) -> List[Node]:
        symbols = {
            '+': TokenType.T_CON,
            '|': TokenType.T_REUN,
            '*': TokenType.T_KLEENE,
            '(': TokenType.T_LPAR,
            ')': TokenType.T_RPAR
            }

        tokens = [Node(symbols['('], '(')]
        for c in s:
            if c in symbols:
                if (c == '(' and                       # adding concatenation inbetween kleene star/letter/right parenthesis and left parenthesis
                    (tokens[-1].tokentype == TokenType.T_KLEENE or
                     tokens[-1].tokentype == TokenType.T_LETTER or
                     tokens[-1].tokentype ==TokenType.T_RPAR)):
                    tokens.append(Node(symbols['+'], '+'))
                if c == '|':
                    tokens.append(Node(symbols[')'], ')'))
                    tokens.append(Node(symbols[c], c))
                    tokens.append(Node(symbols['('], '('))
                else:
                    tokens.append(Node(symbols[c], c))
            elif c.isalpha():
                # adding concatenation in list if current char is a letter and the one before was:
                if ((tokens[-1].tokentype == TokenType.T_LETTER or      # another letter
                    tokens[-1].tokentype == TokenType.T_RPAR or         # a right parenthesis
                    tokens[-1].tokentype == TokenType.T_KLEENE)):       # a kleene star
                    tokens.append(Node(symbols['+'], '+'))
                tokens.append(Node(TokenType.T_LETTER, c))
            else :
                raise Exception('Invalid token: ' + c)

        
        tokens.append(Node(symbols[')'], ')'))
        return tokens

    # creating token list
    tokenList = expressionAnalysis(inString)

    # takes a token list and return a abstract syntax tree
    def toTree(tokenList: List[Node]) -> Node:
        head = None
        while len(tokenList) != 0:
            node = tokenList.pop(0)

            # left parenthesis found in token list
            if node.tokentype == TokenType.T_LPAR:
                if head == None:
                    head = toTree(tokenList)
                else:
                    head.children.append(toTree(tokenList))

            # right parenthesis found in token list
            elif node.tokentype == TokenType.T_RPAR:
                # checking for kleene star
                while len(tokenList) > 0 and tokenList[0].tokentype == TokenType.T_KLEENE:
                    newhead = tokenList.pop(0)
                    newhead.children.append(head)
                    head = newhead
                return head

            # operator + or | found in token list
            elif node.tokentype == TokenType.T_CON or node.tokentype == TokenType.T_REUN:
                node.children.append(head)
                head = node

            # letter found in token list
            else:
                # checking for kleene star
                while len(tokenList) > 0 and tokenList[0].tokentype == TokenType.T_KLEENE:
                    newnode = tokenList.pop(0)
                    newnode.children.append(node)
                    node = newnode

                if (head == None):
                    head = node
                else:
                    head.children.append(node)

        return head

    # return the tree
    tree = toTree(tokenList)

    # DFS for simplifing the tree
    def simplify(node: Node) -> Node:
        if node.tokentype == TokenType.T_LETTER:
            return node
        
        for child in node.children:
            simplify(child)
            
        newChildren = []
        for child in node.children:
            if child.tokentype == node.tokentype:
                newChildren += child.children
            else:
                newChildren.append(child)
        node.children = newChildren

        return node

    return simplify(tree) if simple else tree
