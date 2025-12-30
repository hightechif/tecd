import pytest
from tecd.parser import Parser
from tecd.lexer import Lexer

def parse_text(text):
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()

def test_parser_component():
    text = """
    @circuit
    RES R1 (v=10k)
    @end
    """
    graph = parse_text(text)
    
    # Check graph.components list
    assert any(c.name == "R1" for c in graph.components)
    comp = next(c for c in graph.components if c.name == "R1")
    assert comp.type_name == "RES"
    assert comp.parameters["v"] == "10k"

def test_parser_connection():
    text = """
    @circuit
    RES R1
    RES R2
    R1 -> R2
    @end
    """
    graph = parse_text(text)
    
    # Check connections exist (AST has connections list)
    assert len(graph.connections) > 0
    
    # Check connectivity by inspecting Connection objects
    connected = False
    for conn in graph.connections:
        # conn.source and conn.target are PinReference objects
        s = conn.source.component_name
        t = conn.target.component_name
        if (s == "R1" and t == "R2") or (s == "R2" and t == "R1"):
            connected = True
            break
    assert connected

def test_parser_options():
    text = """
    @circuit
    @options
      layout = vertical
    @end
    @end
    """
    graph = parse_text(text)
    assert graph.options["layout"] == "vertical"
