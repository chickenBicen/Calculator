# this is an exandable calculator project that I'm creating to try and learn new methods of lexing, parsing, and evaluating.
# this project has been written with the help of the internet and AI to explain and learn things that I didn't yet know
# any code that was fully written with ai is fully disclosed

import math
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

# the precedence that unary operators have such that it has more than multiplication but not more than exponentiation
UNARY_PRECEDENCE = 25


FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sqrt": math.sqrt,
    "ln": math.log,
    "log": math.log10,
}

CONSTANTS = {
    "e": math.e,
    "pi": math.pi,
}


# needed to keep things like sin(pi) true
def format_result(value):
    if abs(value) < 1e-15:
        return 0
    return value


# class that loads and saves memory that I want to persist
# variables, functions, previous answers, etc.
class Environment:
    def __init__(self) -> None:
        self.variables: dict[str, float] = {}


##############################################################################
############################### TOKENIZING ###################################
##############################################################################


# Piece of information in the expression ofc ofc
class Token:
    def __init__(self, value, tokentype) -> None:
        self.type = tokentype
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.value}, {self.type})"


# class that tokenizes the initial string expression into smaller pieces
class Lexer:
    def __init__(self, line: str) -> None:
        self.line: str = line  # expression

        # obv just stores the previous token
        self.last_token: Token = Token("", TokenType.NONE)
        self.tokens: list = []  # final output of all the tokens
        self.pos: int = 0  # position we're in across the expression in characters

    # just checks whether or not c is a number
    def check_number(self, c, last_type):
        return c.isdigit()

    # seperating tokenizing of a number from everthing else for readability
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

            elif self.check_number(c, last_type):
                last_type = TokenType.NUMBER
                return self.tokenize_number(value, c, last_type)

            ################### tokenizes identifiers #####################
            elif c.isalpha():
                ident = ""

                while self.pos < len(self.line) and (
                    self.line[self.pos].isalnum() or self.line[self.pos] == "_"
                ):
                    ident += self.line[self.pos]
                    self.pos += 1

                self.last_token = Token(ident, TokenType.IDENTIFIER)
                last_type = self.last_token.type
                return self.last_token

            #################### tokenizes operators ####################

            elif c == "=":
                self.pos += 1
                self.last_token = Token("=", TokenType.EQUAL)
                last_type = self.last_token.type
                return self.last_token

            elif c in ["-", "+", "*", "/", "^"]:
                self.pos += 1
                self.last_token = Token(c, TokenType.OPERATOR)
                last_type = self.last_token.type
                return self.last_token

            elif c == "(":
                self.pos += 1
                self.last_token = Token(c, TokenType.LPAREN)
                last_type = self.last_token.type
                return self.last_token

            elif c == ")":
                self.pos += 1
                self.last_token = Token(c, TokenType.RPAREN)
                last_type = self.last_token.type
                return self.last_token

            else:
                raise SyntaxError("Unknown character")

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


##########################################################################
############################ AST Tree ####################################
##########################################################################


# Base class
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

    def __repr__(self) -> str:
        return self.value


class FunctionCallNode(ASTNode):
    def __init__(self, id: str, arguments: list[ASTNode]) -> None:
        super().__init__()
        self.name = id
        self.arguments = arguments

    def __repr__(self) -> str:
        return f"FunctionCallNode(name: {self.name}, arguments: {self.arguments})"


class AssignmentNode(ASTNode):
    def __init__(self, name: str, right: ASTNode) -> None:
        super().__init__()
        self.name = name
        self.right = right

    def __repr__(self) -> str:
        return f"AssignmentNode(name: {self.name}, right: {self.right})"


##########################################################################
############################### PARSING ##################################
##########################################################################


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def reset(self):
        self.pos = 0

    def handle_explicit_operators(self, left, token, min_precedence):
        operator = token.value
        self.pos += 1

        if OPERATORS[operator]["associativity"] == "right":
            power = OPERATORS[operator]["precedence"]
        else:
            power = OPERATORS[operator]["precedence"] + 1

        right = self.parse(power)
        left = BinaryOperatorNode(operator, left, right)

    def parse(self, min_precedence: int = 0):

        token = self.tokens[self.pos]  # current token

        # parsing parenthesis in their own way separate from precedence

        if token.type == TokenType.LPAREN:
            self.pos += 1
            left = self.parse()

            if (
                self.pos >= len(self.tokens)
                or self.tokens[self.pos].type != TokenType.RPAREN
            ):
                raise SyntaxError("Expected ')'")

            self.pos += 1

        if token.type == TokenType.RPAREN:
            raise SyntaxError("Unexpected ')'")

        # unary - and + handling
        elif token.value in ["-", "+"]:
            self.pos += 1
            left = UnaryOperatorNode(token.value, self.parse(UNARY_PRECEDENCE))

        # handles regular numbers
        elif token.type == TokenType.NUMBER:
            self.pos += 1
            left = NumberNode(token.value)

        # handles identifiers of any kind
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

            if (
                self.pos < len(self.tokens)
                and self.tokens[self.pos].type == TokenType.EQUAL
            ):
                if not isinstance(left, IdentifierNode):
                    raise SyntaxError("assigning something that is not assignable")

                self.pos += 1

                right = self.parse()

                return AssignmentNode(left.value, right)

        # handles operators and gets the rhs of operators
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]

            # Explicit operator
            if token.type == TokenType.OPERATOR:
                if OPERATORS[token.value]["precedence"] < min_precedence:
                    break

                operator = token.value
                self.pos += 1

                if OPERATORS[operator]["associativity"] == "right":
                    power = OPERATORS[operator]["precedence"]
                else:
                    power = OPERATORS[operator]["precedence"] + 1

                right = self.parse(power)
                left = BinaryOperatorNode(operator, left, right)

            # Implicit multiplication
            elif token.type in [
                TokenType.NUMBER,
                TokenType.IDENTIFIER,
                TokenType.LPAREN,
            ]:
                if 20 < min_precedence:
                    break

                right = self.parse(21)
                left = BinaryOperatorNode("*", left, right)

            else:
                break

        return left


###############################################################################
################################ EVALUATION ###################################
###############################################################################


class Evaluator:
    def __init__(self, environment: Environment):
        self.environment = environment

    def evaluate(self, node: ASTNode) -> float:
        if isinstance(node, NumberNode):
            return node.value

        elif isinstance(node, UnaryOperatorNode):
            match node.operator:
                case "-":
                    return -1 * self.evaluate(node.operand)

                case "+":
                    return self.evaluate(node.operand)
                case _:
                    raise SyntaxError("Invalid unary operator")
                    return 0

        elif isinstance(node, BinaryOperatorNode):
            match node.operator:
                case "+":
                    return self.evaluate(node.left) + self.evaluate(node.right)
                case "-":
                    return self.evaluate(node.left) - self.evaluate(node.right)
                case "*":
                    return self.evaluate(node.left) * self.evaluate(node.right)
                case "/":
                    return self.evaluate(node.left) / self.evaluate(node.right)
                case "^":
                    return self.evaluate(node.left) ** self.evaluate(node.right)

                case _:
                    raise SyntaxError("none existant binary operator")
                    return 0

        elif isinstance(node, FunctionCallNode):
            return FUNCTIONS[node.name](self.evaluate(node.arguments[0]))

        elif isinstance(node, IdentifierNode):
            if node.value in self.environment.variables:
                return self.environment.variables[node.value]

            if node.value in CONSTANTS:
                return CONSTANTS[node.value]

            raise NameError(f"Unknown identifier: {node.value}")

        elif isinstance(node, AssignmentNode):
            value = self.evaluate(node.right)
            self.environment.variables[node.name] = value
            return value
        else:
            return 0


class App:
    def __init__(self) -> None:
        self.environment = Environment()

    def run(self):
        while True:
            expression = input(">")

            if expression not in [
                ":help",
                ":variables",
                ":functions",
                ":vars",
                ":funcs",
            ]:
                lexer = Lexer(expression)
                tokens = lexer.tokenize_all()

                parser = Parser(tokens)
                AST_tree_root = parser.parse()

                evaluator = Evaluator(self.environment)
                answer = evaluator.evaluate(AST_tree_root)

                print(answer)

            else:
                match expression:
                    case ":help":
                        print(
                            "type any expression using +-/*^ operators and basic functions like sqrt() and sin()\n Use :funcs to show list of all functions\n Use :vars to show list of all saved variables"
                        )
                    case ":vars" | ":variables":
                        print("CONSTANTS\n-------------------------")
                        for constant, value in CONSTANTS.items():
                            print(f"{constant}: {value}")

                        print("VARIABLES\n-------------------------")
                        for variable, value in self.environment.variables.items():
                            print(f"{variable}: {value}")
                    case ":funcs" | ":functions":
                        print("\n FUNCTIONS\n-------------------------")
                        for function, value in FUNCTIONS.items():
                            print(f"{function}(x)")


environment = Environment()

app = App()

app.run()
