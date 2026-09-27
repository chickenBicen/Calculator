# this is an exandable calculator project that I'm creating to try and learn new methods of lexing, parsing, and evaluating.
# this project has been written with the help of the internet and AI to explain and learn things that I didn't yet know
# any code that was fully written with ai is fully disclosed

from enum import Enum


class TokenType(Enum):
    NONE = 0
    NUMBER = 1
    IDENTIFIER = 2
    EQUAL = 3
    OPERATOR = 4
    FUNCTION = 5
    LPAREN = 6
    RPAREN = 7
    END = 8


OPERATORS = {
    "+": {"precedence": 10, "associativity": "left"},
    "-": {"precedence": 10, "associativity": "left"},
    "*": {"precedence": 20, "associativity": "left"},
    "/": {"precedence": 20, "associativity": "left"},
    "^": {"precedence": 30, "associativity": "right"},
}

UNARY_PRECEDENCE = 25


class Token:
    def __init__(self, value, tokentype) -> None:
        self.type = tokentype
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.value}, {self.type})"


class Lexer:
    def __init__(self, line: str) -> None:
        self.line: str = line
        self.last_token: Token = Token("", TokenType.NONE)
        self.tokens: list = []
        self.pos: int = 0

    def check_number(self, c, last_type):
        return c.isdigit()

    def tokenize_number(self, value, c, last_type):

        while self.pos < len(self.line) and (
            self.line[self.pos].isdigit() or self.line[self.pos] == "."
        ):
            value += self.line[self.pos]
            self.pos += 1

        self.last_token = Token(float(value), TokenType.NUMBER)

        return self.last_token

    def nextToken(self):

        last_type = self.last_token.type
        value = ""

        while self.pos < len(self.line):
            c = self.line[self.pos]

            if c == " ":
                self.pos += 1
                continue

            # if self.line[self.pos:self.pos+3] == "ans":
            #     self.pos += 3
            #
            #     #TODO: add last answer in evaluator

            if self.check_number(c, last_type):
                last_type = TokenType.NUMBER
                return self.tokenize_number(value, c, last_type)

            if c.isalpha():
                ident = ""

                while self.pos < len(self.line) and (
                    self.line[self.pos].isalnum() or self.line[self.pos] == "_"
                ):
                    ident += self.line[self.pos]
                    self.pos += 1

                self.last_token = Token(ident, TokenType.IDENTIFIER)
                last_type = self.last_token.type
                return self.last_token

            if c == "=":
                self.pos += 1
                self.last_token = Token("=", TokenType.EQUAL)
                last_type = self.last_token.type
                return self.last_token

            if c in ["-", "+", "*", "/", "^"]:
                self.pos += 1
                self.last_token = Token(c, TokenType.OPERATOR)
                last_type = self.last_token.type
                return self.last_token

            if c == "(":
                self.pos += 1
                self.last_token = Token(c, TokenType.LPAREN)
                last_type = self.last_token.type
                return self.last_token

            if c == ")":
                self.pos += 1
                self.last_token = Token(c, TokenType.RPAREN)
                last_type = self.last_token.type
                return self.last_token

        self.pos = 0
        self.last_token = Token("", TokenType.NONE)
        return Token("", TokenType.END)

    def tokenize_all(self):
        tokens = []

        while True:
            token = self.nextToken()
            if token.type == TokenType.END:
                break
            tokens.append(token)

        return tokens


class ASTNode:
    def __init__(self) -> None:
        pass


class NumberNode(ASTNode):
    def __init__(self, value: float) -> None:
        super().__init__()
        self.value = value

    def __repr__(self) -> str:
        return f"NumberNode({self.value})"


class BinaryOperatorNode(ASTNode):
    def __init__(self, operator: str, left: ASTNode, right: ASTNode) -> None:
        super().__init__()
        self.operator = operator
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"BinaryOperatorNode(operator: {self.operator}, left: {self.left}, right: {self.right})"


class UnaryOperatorNode(ASTNode):
    def __init__(self, operator: str, operand: ASTNode) -> None:
        super().__init__()
        self.operand = operand
        self.operator = operator

    def __repr__(self) -> str:
        return f"UnaryOperatorNode(operator: {self.operator}, operand: {self.operand})"


class IdentifierNode(ASTNode):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value


class FunctionCallNode(ASTNode):
    def __init__(self, id: str, arguments: list) -> None:
        super().__init__()
        self.name = id
        self.arguments = arguments

    def __repr__(self) -> str:
        return f"FunctionCallNode(name: {self.name}, arguments: [{self.arguments}])"


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def reset(self):
        self.pos = 0

    def parse(self, min_precedence: int = 0):
        token = self.tokens[self.pos]
        if token.type == TokenType.LPAREN:
            self.pos += 1
            left = self.parse()
            if (
                self.pos >= len(self.tokens)
                or self.tokens[self.pos].type != TokenType.RPAREN
            ):
                raise SyntaxError("Expected ')'")

            self.pos += 1

        elif token.value in ["-", "+"]:
            self.pos += 1
            left = UnaryOperatorNode(token.value, self.parse(UNARY_PRECEDENCE))

        elif token.type == TokenType.NUMBER:
            self.pos += 1
            left = NumberNode(token.value)

        elif token.type == TokenType.IDENTIFIER:
            self.pos += 1
            left = IdentifierNode(token.value)

            if (
                self.pos < len(self.tokens)
                and self.tokens[self.pos].type == TokenType.LPAREN
            ):
                self.pos += 1

                argument = self.parse()
                left = FunctionCallNode(left.value, [argument])

                if (
                    self.pos >= len(self.tokens)
                    or self.tokens[self.pos].type != TokenType.RPAREN
                ):
                    raise SyntaxError("Expected ')'")

                self.pos += 1

        while self.pos < len(self.tokens) and (
            self.tokens[self.pos].type == TokenType.OPERATOR
            and OPERATORS[self.tokens[self.pos].value]["precedence"] >= min_precedence
        ):
            operator = self.tokens[self.pos].value
            self.pos += 1

            if OPERATORS[operator]["associativity"] == "right":
                power = OPERATORS[operator]["precedence"]

                right = self.parse(power)
                left = BinaryOperatorNode(operator, left, right)

            else:
                power = OPERATORS[operator]["precedence"] + 1

                right = self.parse(power)
                left = BinaryOperatorNode(operator, left, right)

        return left


# class Evaluator:
#     def __init__(self, root:ASTNode) :
#         self.output = 0
#
#     def evaluate():
#


# !!!!!!!!!!!!!!!!! FULLY AI WRITTEN CODE DISCLOSURE !!!!!!!!!!!!!!!!!!!
def print_tree(root: ASTNode, prefix="", is_left=True):
    if isinstance(root, NumberNode):
        print(prefix + ("└── " if is_left else "┌── ") + str(root.value))
        return

    if isinstance(root, IdentifierNode):
        print(prefix + ("└── " if is_left else "┌── ") + root.value)
        return

    if isinstance(root, UnaryOperatorNode):
        print(prefix + ("└── " if is_left else "┌── ") + root.operator, end="")

        if root.operand:
            print(" ── ", end="")
            print_tree_inline(root.operand)
        else:
            print()

        return

    if isinstance(root, FunctionCallNode):
        print(prefix + ("└── " if is_left else "┌── ") + root.name, end="")

        for argument in root.arguments:
            print(" ── ", end="")
            print_tree_inline(argument)

        print()
        return


def print_tree_inline(root):
    if isinstance(root, NumberNode):
        print(root.value, end="")
        return

    if isinstance(root, IdentifierNode):
        print(root.value, end="")
        return

    if isinstance(root, UnaryOperatorNode):
        print(root.operator, end="")
        print(" ── ", end="")
        print_tree_inline(root.operand)
        return

    if isinstance(root, FunctionCallNode):
        print(root.name, end="")
        for argument in root.arguments:
            print(" ── ", end="")
            print_tree_inline(argument)
        return

    if isinstance(root, BinaryOperatorNode):
        # Binary expressions still need their normal tree structure,
        # so don't try to flatten them here.
        print("(", end="")
        print_tree_inline(root.left)
        print(f" {root.operator} ", end="")
        print_tree_inline(root.right)
        print(")", end="")


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


input = input()

lexer = Lexer(input)

tokens = lexer.tokenize_all()

for i in tokens:
    print(i)

parser = Parser(tokens)

print(parser.parse(), "\n")

parser.reset()

print_tree(parser.parse())
