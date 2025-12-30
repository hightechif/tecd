from dataclasses import dataclass, field
from typing import List, Optional, Dict, Union

@dataclass
class SourceLocation:
    line: int
    column: int

@dataclass(kw_only=True)
class ASTNode:
    location: Optional[SourceLocation] = None

@dataclass(kw_only=True)
class Parameter(ASTNode):
    key: str
    value: str

@dataclass(kw_only=True)
class Component(ASTNode):
    type_name: str
    name: str
    parameters: Dict[str, str]

@dataclass(kw_only=True)
class PinReference(ASTNode):
    component_name: str
    pin_name: Optional[str] = None

@dataclass(kw_only=True)
class Connection(ASTNode):
    source: PinReference
    target: PinReference

@dataclass(kw_only=True)
class Option(ASTNode):
    key: str
    value: str

@dataclass(kw_only=True)
class Circuit(ASTNode):
    components: List[Component] = field(default_factory=list)
    connections: List[Connection] = field(default_factory=list)
    options: Dict[str, str] = field(default_factory=dict)
