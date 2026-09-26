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
        return c.isdigit() or (
            c == "-"
            and (
                last_type == TokenType.NONE
                or last_type == TokenType.LPAREN
                or last_type == TokenType.OPERATOR
            )
        )

    def tokenize_number(self, value, c, last_type):

        is_negative = False
        if c == "-":
            is_negative = True
            self.pos += 1

        while self.pos < len(self.line) and (
            self.line[self.pos].isdigit() or self.line[self.pos] == "."
        ):
            value += self.line[self.pos]
            self.pos += 1

        if is_negative:
            value = "-" + value

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
                # TODO: identifiers and such
                pass

            if c == "=":
                self.pos += 1
                self.last_token = Token("=", TokenType.EQUAL)
                last_type = self.last_token.type
                return self.last_token

            if c in ["-", "+", "*", "/"]:
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


input = input()

lexer = Lexer(input)

tokens = lexer.tokenize_all()

for i in tokens:
    print(i)
