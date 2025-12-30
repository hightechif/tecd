from typing import Dict, List
import math
from .semantics import CircuitGraph, Net
from .layout import Layout, PlacedComponent
from .symbols import get_symbol

class SVGRenderer:
    def __init__(self, graph: CircuitGraph, layout: Layout):
        self.graph = graph
        self.layout = layout
        self.comp_map = {pc.component.name: pc for pc in layout.components}

    def render(self) -> str:
        lines = []
        lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.layout.width}" height="{self.layout.height}" viewBox="0 0 {self.layout.width} {self.layout.height}">')
        lines.append('<style> text { font-family: sans-serif; fill: black; } path, line, rect { stroke: black; } </style>')
        lines.append('<rect width="100%" height="100%" fill="white"/>') # Background

        # Draw Components
        for pc in self.layout.components:
            symbol = get_symbol(pc.component.type_name)
            lines.append(f'<g transform="translate({pc.x}, {pc.y}) rotate({pc.rotation})">')
            lines.append(f'  <g class="symbol">{symbol.path}</g>')
            
            # Draw Labels
            # Counter-rotate text to keep it horizontal
            lx, ly = symbol.label_offset
            rot_attr = f'transform="rotate({-pc.rotation}, {lx}, {ly})"' if pc.rotation else ''
            lines.append(f'  <text x="{lx}" y="{ly}" text-anchor="middle" font-size="12" {rot_attr}>{pc.component.name}</text>')
            
            # Parameters
            param_txt = " ".join([v for k,v in pc.component.parameters.items()])
            py = symbol.label_offset[1] + 55
            rot_attr_p = f'transform="rotate({-pc.rotation}, {lx}, {py})"' if pc.rotation else ''
            lines.append(f'  <text x="{lx}" y="{py}" text-anchor="middle" font-size="10" fill="gray" {rot_attr_p}>{param_txt}</text>')
            
            lines.append('</g>')

        # Draw Wires (Nets)
        for net in self.graph.nets:
            points = []
            for ref in net.points:
                if ref.component.name not in self.comp_map: continue
                
                pc = self.comp_map[ref.component.name]
                symbol = get_symbol(pc.component.type_name)
                pin_offset = symbol.pins.get(ref.pin_name, (0,0))
                
                # Apply rotation to pin_offset
                if pc.rotation:
                    rad = math.radians(pc.rotation)
                    px, py = pin_offset
                    rot_x = px * math.cos(rad) - py * math.sin(rad)
                    rot_y = px * math.sin(rad) + py * math.cos(rad)
                    pin_offset = (rot_x, rot_y)
                
                abs_x = pc.x + pin_offset[0]
                abs_y = pc.y + pin_offset[1]
                points.append((abs_x, abs_y))
            
            if len(points) >= 2:
                for i in range(len(points) - 1):
                    p1 = points[i]
                    p2 = points[i+1]
                    x1, y1 = p1
                    x2, y2 = p2
                    
                    style = getattr(self.layout, 'routing_style', 'straight')
                    
                    if style == 'straight' or (abs(x1-x2) < 1 and abs(y1-y2) < 1):
                         lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="blue" stroke-width="1" />')
                    else:
                        d = ""
                        if style == 'HV': # Horizontal then Vertical
                            d = f"M {x1} {y1} L {x2} {y1} L {x2} {y2}"
                        elif style == 'VH': # Vertical then Horizontal
                            d = f"M {x1} {y1} L {x1} {y2} L {x2} {y2}"
                        
                        if d:
                            lines.append(f'<path d="{d}" stroke="blue" stroke-width="1" fill="none"/>')
                        else: # Fallback
                             lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="blue" stroke-width="1" />')

        lines.append('</svg>')
        return "\n".join(lines)

def render_svg(graph: CircuitGraph, layout: Layout) -> str:
    return SVGRenderer(graph, layout).render()
