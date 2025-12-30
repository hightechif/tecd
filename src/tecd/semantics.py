from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from .ast_nodes import Circuit, Component, Connection, PinReference

@dataclass
class Net:
    id: str
    points: List['ResolvedPin'] = field(default_factory=list)

@dataclass
class ResolvedPin:
    component: Component
    pin_name: str

@dataclass
class CircuitGraph:
    components: Dict[str, Component]
    nets: List[Net]
    options: Dict[str, str]

# Default Pin Definitions
DEFAULT_PINS = {
    'RES': ('left', 'right'),
    'CAP': ('top', 'bottom'),
    'IND': ('left', 'right'),
    'VDC': ('-', '+'),
    'GND': ('0',),
    'DIODE': ('anode', 'cathode'),
    'LED': ('anode', 'cathode'),
    'SWITCH': ('1', '2'),
    'VAC': ('+', '-'),
    'IDC': ('+', '-')
}

class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self, ast: Circuit):
        self.ast = ast
        self.components: Dict[str, Component] = {}
        self.nets: List[Net] = []
        self._next_net_id = 1

    def analyze(self) -> CircuitGraph:
        self._collect_components()
        self._resolve_connections()
        return CircuitGraph(self.components, self.nets, self.ast.options)

    def _collect_components(self):
        for comp in self.ast.components:
            if comp.name in self.components:
                 raise SemanticError(f"Duplicate component name '{comp.name}' defined at line {comp.location.line}")
            self.components[comp.name] = comp
            
        # Ensure GND exists if used implicitly (though it is reserved)
        # We can treat 'GND' as a special global component or just allow it.
        # For this implementation, let's say GND is always available as a 'GND' type component named 'GND' if not explicitly defined.
        if 'GND' not in self.components:
             # Implicit GND
             self.components['GND'] = Component(type_name='GND', name='GND', parameters={})

    def _resolve_connections(self):
        # We need to flatten chains: A -> B -> C becomes (A, B) and (B, C)
        # And resolve default pins.
        
        # This is a simplified "netlist" approach where each connection creates a 2-point net
        # OR we merge connected nets. We need explicit nodes/nets.
        
        # Let's map (Component, Pin) to a Net object.
        pin_map: Dict[str, Dict[str, Net]] = {} # comp_name -> pin_name -> Net

        def get_or_create_net(comp_name: str, pin_name: str) -> Net:
            if comp_name not in pin_map:
                pin_map[comp_name] = {}
            
            if pin_name in pin_map[comp_name]:
                return pin_map[comp_name][pin_name]
            
            new_net = Net(id=f"N{self._next_net_id}")
            self._next_net_id += 1
            pin_map[comp_name][pin_name] = new_net
            self.nets.append(new_net)
            return new_net
            
        def merge_nets(net1: Net, net2: Net):
            if net1 is net2: return
            
            # Move all points from net2 to net1
            # Update pin_map for all points in net2
            for point in net2.points:
                pin_map[point.component.name][point.pin_name] = net1
                net1.points.append(point)
            
            if net2 in self.nets:
                self.nets.remove(net2)

        for conn in self.ast.connections:
            # Resolve Source Pin
            source_comp = self._get_component(conn.source.component_name)
            source_pin = self._resolve_pin(source_comp, conn.source.pin_name, is_source=True)
            
            # Resolve Target Pin
            target_comp = self._get_component(conn.target.component_name)
            target_pin = self._resolve_pin(target_comp, conn.target.pin_name, is_source=False)
            
            # Create/Get nets and merge them
            net_source = get_or_create_net(source_comp.name, source_pin)
            net_target = get_or_create_net(target_comp.name, target_pin)
            
            # Add points to nets if not already there (for newly created nets)
            if not any(p.component == source_comp and p.pin_name == source_pin for p in net_source.points):
                net_source.points.append(ResolvedPin(source_comp, source_pin))
                
            if not any(p.component == target_comp and p.pin_name == target_pin for p in net_target.points):
                 net_target.points.append(ResolvedPin(target_comp, target_pin))

            merge_nets(net_source, net_target)

    def _get_component(self, name: str) -> Component:
        if name not in self.components:
             # Special case for implicit nets? The spec says "Nets are implicit objects" (e.g. N1)
             # "Nets represent electrical nodes". If a user uses N1 as a pseudo-component, 
             # it essentially just acts as a named junction.
             # Let's treat it as a "Net" component for now if it helps, or check if it matches Net naming?
             # Spec: "V1 -> R1 -> N1"
             
             # If it starts with 'N' followed by digits/etc? Or just allow any undefined ID to be a Net Node?
             # Spec says "Nets are implicit objects".
             # For now, if not in components, treat as a virtual Junction component.
             self.components[name] = Component(type_name='JUNCTION', name=name, parameters={})
             
        return self.components[name]

    def _resolve_pin(self, comp: Component, pin_name: Optional[str], is_source: bool) -> str:
        if pin_name:
            return pin_name
        
        # Default pin logic
        comp_type = comp.type_name
        
        if comp_type == 'JUNCTION':
            return '0' # Junctions effectively have 1 pin, connected on all sides.
            
        if comp_type not in DEFAULT_PINS:
             raise SemanticError(f"Component type '{comp_type}' has no default pins. Specify pin explicitly for '{comp.name}'.")
             
        pins = DEFAULT_PINS[comp_type]
        
        # If Ground, always 0
        if comp_type == 'GND':
            return '0'
            
        # Linear chain logic: "V1 -> R1" means "V1.+ -> R1.left" (Source -> Target?)
        # Wait, spec says: "V1 -> R1 -> C1 -> GND" -> "V1.+ -> R1.left", "R1.right -> C1.top"
        # Source uses OUT pin, Target uses IN pin?
        # But for 2-pin passives, it's conventional.
        
        # Spec Table:
        # RES: left, right
        # CAP: top, bottom
        
        # If is_source (left side of ->), use the "right" or "bottom" or "second" pin?
        # No, "V1 -> R1"
        # V1 is source. V1.+ is used. (Wait, V1 is VDC, pins +, -). usually + is top/source.
        # R1 is target. R1.left is used.
        # Next connection: "R1 -> C1"
        # R1 is source. R1.right is used.
        # C1 is target. C1.top is used.
        
        # Heuristic:
        # If Target: use index 0 (left/top/+/anode)
        # If Source: use index 1 (right/bottom/-/cathode)
        
        if len(pins) < 2:
             if len(pins) == 1: return pins[0] # e.g. GND
             raise SemanticError(f"Cannot imply pin for '{comp.name}'")
             
        return pins[1] if is_source else pins[0]

def analyze(ast: Circuit) -> CircuitGraph:
    return SemanticAnalyzer(ast).analyze()
