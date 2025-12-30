from typing import List, Optional
from .ast_nodes import Circuit, Component, Connection, Option, PinReference, SourceLocation
from .lexer import Token, TokenType, tokenize

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_circuit = Circuit()

    def current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def advance(self) -> Token:
        token = self.current()
        if self.pos < len(self.tokens):
            self.pos += 1
        return token

    def peek(self) -> Token:
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return self.tokens[-1]

    def match(self, token_type: str) -> bool:
        if self.current().type == token_type:
            self.advance()
            return True
        return False

    def expect(self, token_type: str) -> Token:
        if self.current().type == token_type:
            return self.advance()
        raise SyntaxError(f"Expected {token_type} at {self.current().line}:{self.current().column}, found {self.current().type}")

    def parse(self) -> Circuit:
        while self.current().type == TokenType.NEWLINE:
            self.advance()
        self.expect(TokenType.KW_CIRCUIT)
        
        while self.current().type != TokenType.KW_END and self.current().type != TokenType.EOF:
            self.parse_statement()
        
        self.expect(TokenType.KW_END)
        return self.current_circuit

    def parse_statement(self):
        token = self.current()
        
        if token.type == TokenType.KW_OPTIONS:
            self.parse_options()
        elif token.type == TokenType.TYPE:
            # Ambiguity check for GND (can be TYPE or PinRef)
            # If GND is followed by ARROW or DOT, it's a connection chain
            if token.value == 'GND' and self.peek().type in [TokenType.ARROW, TokenType.DOT]:
                self.parse_connection_chain()
            else:
                self.parse_component()
        elif token.type == TokenType.ID:
            self.parse_connection_chain()
        elif token.type == TokenType.NEWLINE:
            self.advance()
        else:
             raise SyntaxError(f"Unexpected token {token.type} at {token.line}:{token.column}")

    def parse_options(self):
        self.advance() # Skip @options
        
        while self.current().type != TokenType.KW_END:
             if self.current().type == TokenType.NEWLINE:
                 self.advance()
                 continue
                 
             key = self.expect(TokenType.ID).value
             self.expect(TokenType.EQUALS)
             value = self.expect(TokenType.ID).value # Options values are IDs for now
             
             self.current_circuit.options[key] = value
        
        self.expect(TokenType.KW_END)

    def parse_component(self):
        type_token = self.advance()
        name_token = self.expect(TokenType.ID)
        
        params = {}
        if self.match(TokenType.LPAREN):
            while self.current().type != TokenType.RPAREN:
                 if self.current().type == TokenType.NEWLINE: # Handle newlines in params
                     self.advance()
                     continue
                 
                 key = self.expect(TokenType.ID).value
                 self.expect(TokenType.EQUALS)
                 
                 # Value can be string token (for 10k, 5V) or just ID if simple
                 val_token = self.current()
                 if val_token.type in [TokenType.STRING, TokenType.ID]:
                     value = val_token.value
                     self.advance()
                 else:
                     raise SyntaxError(f"Expected value at {val_token.line}:{val_token.column}")
                     
                 params[key] = value
            self.expect(TokenType.RPAREN)
            
        self.current_circuit.components.append(Component(
            location=SourceLocation(type_token.line, type_token.column),
            type_name=type_token.value,
            name=name_token.value,
            parameters=params
        ))

    def parse_connection_chain(self):
        # A -> B -> C -> D
        # Start with parsing one pin ref
        left_ref = self.parse_pin_reference()
        
        while self.match(TokenType.ARROW):
            right_ref = self.parse_pin_reference()
            
            self.current_circuit.connections.append(Connection(
                source=left_ref,
                target=right_ref
            ))
            
            # Prepare for next link in chain: current right becomes next left
            left_ref = right_ref

    def parse_pin_reference(self) -> PinReference:
        token = self.current()
        if token.type == TokenType.ID:
            name_token = self.advance()
        elif token.type == TokenType.TYPE and token.value == 'GND':
            name_token = self.advance()
        else:
            raise SyntaxError(f"Expected ID or GND at {token.line}:{token.column}, found {token.type}")
            
        component_name = name_token.value
        pin_name = None
        
        if self.match(TokenType.DOT):
            pin_name_token = self.current()
            if pin_name_token.type in [TokenType.ID, TokenType.STRING]: # Pins can be numbers like "0" for GND
                 pin_name = pin_name_token.value
                 self.advance()
            else:
                 raise SyntaxError(f"Expected pin name at {pin_name_token.line}:{pin_name_token.column}")
                 
        return PinReference(component_name=component_name, pin_name=pin_name)

def parse(source: str) -> Circuit:
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse()
