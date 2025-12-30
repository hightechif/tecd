import re
from dataclasses import dataclass
from typing import List, Generator

@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int

class TokenType:
    KW_CIRCUIT = 'KW_CIRCUIT'
    KW_END = 'KW_END'
    KW_OPTIONS = 'KW_OPTIONS'
    TYPE = 'TYPE'  # VDC, RES, CAP, IND, etc.
    ID = 'ID'
    ARROW = 'ARROW'   # ->
    DOT = 'DOT'       # .
    EQUALS = 'EQUALS' # =
    LPAREN = 'LPAREN' # (
    RPAREN = 'RPAREN' # )
    NEWLINE = 'NEWLINE'
    EOF = 'EOF'
    STRING = 'STRING' # For values like "1k", "5V"

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.current_line = 1
        self.current_col = 1
    
    def tokenize(self) -> List[Token]:
        pos = 0
        while pos < len(self.source):
            match = None
            
            # Skip whitespace (except newline)
            if self.source[pos] in ' \t':
                self.current_col += 1
                pos += 1
                continue
            
            # Comments
            if self.source[pos] == '#':
                while pos < len(self.source) and self.source[pos] != '\n':
                    pos += 1
                continue
            
            # Newline
            if self.source[pos] == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.current_line, self.current_col))
                self.current_line += 1
                self.current_col = 1
                pos += 1
                continue

            # Operators (Arrow must be checked before IDs/Values because '-' can be start of ID)
            if self.source.startswith('->', pos):
                self.tokens.append(Token(TokenType.ARROW, '->', self.current_line, self.current_col))
                self.current_col += 2
                pos += 2
                continue

            # Keywords / Identifiers / Types / Values
            # Allow + and - to start an ID (e.g. V+.pin, -5V)
            if self.source[pos].isalpha() or self.source[pos] in '@+-%0-9': 
                 # Regex for ID/Value: alphanumeric, _, %, +, -
                match = re.match(r'(@?[a-zA-Z0-9_%+-]+)', self.source[pos:])
                if match:
                    val = match.group(1)
                    token_type = TokenType.ID
                    
                    if val == '@circuit': token_type = TokenType.KW_CIRCUIT
                    elif val == '@end': token_type = TokenType.KW_END
                    elif val == '@options': token_type = TokenType.KW_OPTIONS
                    elif val in ['VDC', 'RES', 'CAP', 'IND', 'GND', 'DIODE', 'LED', 'SWITCH', 'VAC', 'IDC',
                                 'NPN', 'PNP', 'NMOS', 'PMOS', 'AND', 'OR', 'NOT', 'NAND']: 
                        token_type = TokenType.TYPE
                    # Fallback ID for values or pin names
                    
                    self.tokens.append(Token(token_type, val, self.current_line, self.current_col))
                    self.current_col += len(val)
                    pos += len(val)
                    continue
                
            char = self.source[pos]
            if char == '.':
                self.tokens.append(Token(TokenType.DOT, '.', self.current_line, self.current_col))
            elif char == '=':
                self.tokens.append(Token(TokenType.EQUALS, '=', self.current_line, self.current_col))
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', self.current_line, self.current_col))
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', self.current_line, self.current_col))
            else:
                # Fallback for values (can contain numbers, percent, etc.)
                # This is a bit loose, refinement might be needed for strict parsing
                match = re.match(r'([a-zA-Z0-9%\.]+)', self.source[pos:])
                if match:
                    val = match.group(1)
                    self.tokens.append(Token(TokenType.STRING, val, self.current_line, self.current_col))
                    self.current_col += len(val)
                    pos += len(val)
                    continue
                else:
                    raise SyntaxError(f"Unexpected character '{char}' at {self.current_line}:{self.current_col}")
            
            self.current_col += 1
            pos += 1

        self.tokens.append(Token(TokenType.EOF, '', self.current_line, self.current_col))
        return self.tokens

def tokenize(source: str) -> List[Token]:
    return Lexer(source).tokenize()
