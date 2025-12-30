import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Set, Deque, Tuple
from collections import deque, defaultdict
from .semantics import CircuitGraph, Component, Net
from .symbols import get_symbol

@dataclass
class PlacedComponent:
    component: Component
    x: float
    y: float
    symbol_ref: str
    rotation: float = 0.0

@dataclass
class Layout:
    components: List[PlacedComponent]
    width: float
    height: float
    routing_style: str = 'straight' # 'straight', 'HV', 'VH'

class LayoutEngine:
    def __init__(self, graph: CircuitGraph):
        self.graph = graph

    def layout(self) -> Layout:
        mode = self.graph.options.get('layout', 'automatic').strip().lower()
        
        if mode == 'vertical':
            return self.rank_layout(direction='vertical')
        elif mode == 'horizontal':
            return self.rank_layout(direction='horizontal')
        else:
            return self.force_layout(direction='horizontal')
    def rank_layout(self, direction: str) -> Layout:
        # 1. Build Adjacency Graph
        adj: Dict[str, Set[str]] = defaultdict(set)
        for net in self.graph.nets:
            comps_in_net = [p.component.name for p in net.points]
            for i in range(len(comps_in_net)):
                for j in range(i + 1, len(comps_in_net)):
                    c1, c2 = comps_in_net[i], comps_in_net[j]
                    if c1 != c2:
                        adj[c1].add(c2)
                        adj[c2].add(c1)

        # 2. Assign Ranks (BFS)
        start_nodes = []
        for name, comp in self.graph.components.items():
            if comp.type_name == 'JUNCTION': continue
            if comp.type_name.startswith('V') or comp.type_name.startswith('I'):
                start_nodes.append(name)
        
        if not start_nodes and self.graph.components:
             first = next((c.name for c in self.graph.components.values() if c.type_name != 'JUNCTION'), None)
             if first: start_nodes.append(first)

        ranks: Dict[str, int] = {}
        visited: Set[str] = set()
        
        for root in start_nodes:
            if root in visited: continue
            
            queue: Deque[str] = deque([root])
            visited.add(root)
            ranks[root] = 0
            
            while queue:
                node = queue.popleft()
                current_rank = ranks[node]
                neighbors = adj[node]
                sorted_neighbors = sorted(list(neighbors))
                
                for neighbor in sorted_neighbors:
                    if neighbor not in visited and self.graph.components[neighbor].type_name != 'JUNCTION':
                        ranks[neighbor] = current_rank + 1
                        visited.add(neighbor)
                        queue.append(neighbor)
        
        for name, comp in self.graph.components.items():
             if name not in visited and comp.type_name != 'JUNCTION':
                 ranks[name] = 0
                 visited.add(name)
                 queue: Deque[str] = deque([name])
                 while queue:
                    node = queue.popleft()
                    current_rank = ranks[node]
                    for neighbor in sorted(list(adj[node])):
                        if neighbor not in visited and self.graph.components[neighbor].type_name != 'JUNCTION':
                             ranks[neighbor] = current_rank + 1
                             visited.add(neighbor)
                             queue.append(neighbor)

        # 3. Create Coordinates
        layers: Dict[int, List[str]] = defaultdict(list)
        for name, rank in ranks.items():
            layers[rank].append(name)

        placed_components = []
        H_SPACING = 150
        V_SPACING = 120
        START_X = 100
        START_Y = 100
        
        # Calculate grid size
        max_rank = max(layers.keys()) if layers else 0
        
        for rank in sorted(layers.keys()):
            nodes = layers[rank]
            
            # GND logic: push to end
            gnds = [n for n in nodes if self.graph.components[n].type_name == 'GND']
            others = [n for n in nodes if self.graph.components[n].type_name != 'GND']
            ordered_nodes = others + gnds
            
            for i, name in enumerate(ordered_nodes):
                comp = self.graph.components[name]
                
                # Determine position and rotation based on direction
                if direction == 'horizontal':
                    x = START_X + rank * H_SPACING
                    y = START_Y + i * V_SPACING
                    rotation = 0.0
                    if comp.type_name == 'GND':
                         y += 60 # Offset GND down for elbow
                else: # vertical
                    x = START_X + i * H_SPACING # Spread horizontally
                    y = START_Y + rank * V_SPACING # Flow down
                    rotation = 90.0
                    if comp.type_name == 'GND':
                         y += 60 # Vertical needs offset? Maybe not, usually straight down.
                         rotation = 0.0

                placed_components.append(PlacedComponent(
                    component=comp,
                    x=x,
                    y=y,
                    symbol_ref=comp.type_name,
                    rotation=rotation
                ))

        # Size estimation
        if direction == 'horizontal':
             width = START_X + (max_rank + 1) * H_SPACING
             height = START_Y + 500
             routing = 'HV'
        else:
             width = START_X + 500
             height = START_Y + (max_rank + 1) * V_SPACING
             routing = 'VH'

        return Layout(
            components=placed_components,
            width=width,
            height=height,
            routing_style=routing
        )

    def force_layout(self, direction: str = 'horizontal') -> Layout:
        # Simple Fruchterman-Reingold inspired layout
        nodes = [name for name, c in self.graph.components.items() if c.type_name != 'JUNCTION']
        if not nodes: return Layout([], 100, 100)

        # Initialize positions (Circle or Random)
        positions: Dict[str, Tuple[float, float]] = {}
        width = 800
        height = 600
        if direction == 'vertical':
             width, height = 600, 800
             
        center_x, center_y = width / 2, height / 2
        radius = 200
        
        for i, node in enumerate(nodes):
             angle = 2 * math.pi * i / len(nodes)
             positions[node] = (center_x + radius * math.cos(angle), center_y + radius * math.sin(angle))
        
        # Fixed nodes strategies based on direction
        fixed_nodes = set()
        for node in nodes:
             comp = self.graph.components[node]
             if direction == 'horizontal':
                 # Pin Voltage source to Left
                 if comp.type_name.startswith('V'):
                     positions[node] = (100, center_y)
                     fixed_nodes.add(node)
                 # Pin Ground to Right (or Bottom-Right?)
                 elif comp.type_name == 'GND':
                     positions[node] = (width - 100, center_y + 100) # Slightly down
                     fixed_nodes.add(node)
             else: # vertical
                 # Pin Voltage source to Top
                 if comp.type_name.startswith('V'):
                     positions[node] = (center_x, 100)
                     fixed_nodes.add(node)
                 # Pin Ground to Bottom
                 elif comp.type_name == 'GND':
                     positions[node] = (center_x, height - 100)
                     fixed_nodes.add(node)

        # Build edges
        edges = []
        for net in self.graph.nets:
            comps = [p.component.name for p in net.points if p.component.name in nodes]
            for i in range(len(comps)):
                for j in range(i+1, len(comps)):
                     edges.append((comps[i], comps[j]))
        
        # Iterations
        iterations = 2000
        k = math.sqrt(width * height / len(nodes)) * 1.5
        
        # Temperature
        t = width / 10
        dt = t / (iterations + 1)

        for it in range(iterations):
            disp = {node: [0.0, 0.0] for node in nodes}
            
            # Repulsion
            for i in range(len(nodes)):
                n1 = nodes[i]
                for j in range(i+1, len(nodes)):
                    n2 = nodes[j]
                    dx = positions[n1][0] - positions[n2][0]
                    dy = positions[n1][1] - positions[n2][1]
                    dist = math.sqrt(dx*dx + dy*dy) or 0.1
                    
                    repulse = (k * k) / dist
                    
                    disp[n1][0] += (dx / dist) * repulse
                    disp[n1][1] += (dy / dist) * repulse
                    disp[n2][0] -= (dx / dist) * repulse
                    disp[n2][1] -= (dy / dist) * repulse
            
            # Attraction
            for u, v in edges:
                dx = positions[u][0] - positions[v][0]
                dy = positions[u][1] - positions[v][1]
                dist = math.sqrt(dx*dx + dy*dy) or 0.1
                
                attract = (dist * dist) / k
                
                disp[u][0] -= (dx / dist) * attract
                disp[u][1] -= (dy / dist) * attract
                disp[v][0] += (dx / dist) * attract
                disp[v][1] += (dy / dist) * attract
            
            # Apply
            for node in nodes:
                if node in fixed_nodes: continue
                
                d = math.sqrt(disp[node][0]**2 + disp[node][1]**2) or 0.1
                
                positions[node] = (
                    positions[node][0] + (disp[node][0] / d) * min(d, t),
                    positions[node][1] + (disp[node][1] / d) * min(d, t)
                )
                
                # Weak Gravity
                positions[node] = (
                    positions[node][0] + (center_x - positions[node][0]) * 0.01 * (t/width),
                    positions[node][1] + (center_y - positions[node][1]) * 0.01 * (t/width)
                )

                positions[node] = (
                    max(50, min(width - 50, positions[node][0])),
                    max(50, min(height - 50, positions[node][1]))
                )
            
            t -= dt
        
        # Post-Processing: Grid Snapping
        GRID_SIZE = 40
        for node in nodes:
            x, y = positions[node]
            positions[node] = (round(x / GRID_SIZE) * GRID_SIZE, round(y / GRID_SIZE) * GRID_SIZE)

        # Calculate Rotations
        rotations: Dict[str, float] = {}
        for node in nodes:
            comp = self.graph.components[node]
            connected_nets = [net for net in self.graph.nets if any(p.component.name == node for p in net.points)]
            
            if len(connected_nets) == 2:
                 net1_points = [p for p in connected_nets[0].points if p.component.name != node and p.component.name in positions]
                 net2_points = [p for p in connected_nets[1].points if p.component.name != node and p.component.name in positions]
                 
                 if net1_points and net2_points:
                     n1 = net1_points[0].component.name
                     n2 = net2_points[0].component.name
                     
                     x1, y1 = positions[n1]
                     x2, y2 = positions[n2]
                     
                     angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
                     # Snap rotation to nearest 45 degrees
                     rotations[node] = round(angle / 45) * 45
            
        placed = []
        for node in nodes:
            placed.append(PlacedComponent(
                component=self.graph.components[node],
                x=positions[node][0],
                y=positions[node][1],
                symbol_ref=self.graph.components[node].type_name,
                rotation=rotations.get(node, 0.0)
            ))
            
        return Layout(placed, width, height, routing_style='straight')

def compute_layout(graph: CircuitGraph) -> Layout:
    return LayoutEngine(graph).layout()
