import pytest
from tecd.lexer import Lexer, TokenType

def test_lexer_basic():
    text = "RES R1 (v=1k)"
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    
    # RES is a known type, so it gets TokenType.TYPE
    assert tokens[0].type == TokenType.TYPE
    assert tokens[0].value == "RES"
    
    assert tokens[1].type == TokenType.ID
    assert tokens[1].value == "R1"
    
    assert tokens[2].type == TokenType.LPAREN
    assert tokens[3].type == TokenType.ID
    assert tokens[3].value == "v"
    
    assert tokens[4].type == TokenType.EQUALS
    
    # "1k" stars with digit, likely STRING in this lexer
    assert tokens[5].type == TokenType.STRING
    assert tokens[5].value == "1k"
    
    assert tokens[6].type == TokenType.RPAREN
    assert tokens[7].type == TokenType.EOF

def test_lexer_connection():
    text = "A -> B"
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    
    assert tokens[0].value == "A"
    assert tokens[1].type == TokenType.ARROW
    assert tokens[2].value == "B"

def test_lexer_options():
    text = "@options layout=horizontal @end"
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    
    identifiers = [t.value for t in tokens if t.type == TokenType.ID]
    assert "layout" in identifiers
    assert "horizontal" in identifiers
