from .parser import parse
from .semantics import analyze, CircuitGraph

def compile(source: str) -> CircuitGraph:
    ast = parse(source)
    graph = analyze(ast)
    return graph
