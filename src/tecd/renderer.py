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
            # Determine Screen Offsets based on orientation
            # Default (Horizontal 0): Name Top (0, -30), Params Bottom (0, 30)
            # Vertical (-90/270 or 90): Name Left (-35, 0), Params Right (35, 0)
            
            # Normalize rotation to 0-360 or -180-180
            rot = pc.rotation % 360
            
            # Define target SCREEN offsets
            if pc.component.type_name == 'GND':
                # GND Special Case: Name Left and slightly Up
                name_screen_offset = (-30, -15)
                param_screen_offset = (30, 0)
            elif 45 <= rot <= 135 or 225 <= rot <= 315: # Vertical-ish (90 or 270/-90)
                # Vertical
                name_screen_offset = (-35, 0)
                param_screen_offset = (35, 0)
            else:
                # Horizontal
                name_screen_offset = (0, -30)
                param_screen_offset = (0, 30)
                
            # Transform Screen Offsets to Local Offsets
            # Local = Rotate(+Rot) * Screen
            # Because Screen = Rotate(-Rot) * Local
            
            # Wait, Rotation Matrix R(theta) maps Local -> Screen
            # So Screen = R(rot) * Local
            # Local = R(-rot) * Screen
            
            rad = math.radians(-pc.rotation)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            
            def to_local(ox, oy):
                return (ox * cos_a - oy * sin_a, ox * sin_a + oy * cos_a)
                
            lx, ly = to_local(*name_screen_offset)
            px, py = to_local(*param_screen_offset)

            # Text rotation correction: 
            # The group is rotated by -pc.rotation (SVG CW).
            # To keep text upright, we must rotate text by +pc.rotation (relative to group).
            
            rot_attr = f'transform="rotate({-pc.rotation}, {lx}, {ly})"'
            rot_attr_p = f'transform="rotate({-pc.rotation}, {px}, {py})"'

            lines.append(f'  <text x="{lx}" y="{ly}" text-anchor="middle" font-size="12" dominant-baseline="middle" {rot_attr}>{pc.component.name}</text>')
            
            # Parameters
            param_txt = " ".join([v for k,v in pc.component.parameters.items()])
            lines.append(f'  <text x="{px}" y="{py}" text-anchor="middle" font-size="10" fill="gray" dominant-baseline="middle" {rot_attr_p}>{param_txt}</text>')
            
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
                    if style == 'HV': # Horizontal Layout (Horizontal -> Vertical -> Horizontal)
                        # Check for GND connection (Special Case)
                        is_p1_gnd = self.comp_map.get(net.points[i].component.name) and self.comp_map[net.points[i].component.name].component.type_name == 'GND'
                        is_p2_gnd = self.comp_map.get(net.points[i+1].component.name) and self.comp_map[net.points[i+1].component.name].component.type_name == 'GND'
                        
                        if is_p2_gnd: 
                            # Terminating at GND: Horizontal then Vertical (Elbow to bottom)
                            # M x1 y1 L x2 y1 L x2 y2
                            d = f"M {x1} {y1} L {x2} {y1} L {x2} {y2}"
                        elif is_p1_gnd:
                            # Starting from GND: Vertical then Horizontal (Elbow from bottom)
                            # M x1 y1 L x1 y2 L x2 y2
                            d = f"M {x1} {y1} L {x1} {y2} L {x2} {y2}"
                        else:
                            # Standard Z-routing
                            mid_x = (x1 + x2) / 2
                            d = f"M {x1} {y1} L {mid_x} {y1} L {mid_x} {y2} L {x2} {y2}"
                    elif style == 'VH': # Vertical Layout (Vertical -> Horizontal -> Vertical)
                        # Use Z-routing
                        mid_y = (y1 + y2) / 2
                        d = f"M {x1} {y1} L {x1} {mid_y} L {x2} {mid_y} L {x2} {y2}"
                        
                    if d:
                        lines.append(f'<path d="{d}" stroke="blue" stroke-width="1" fill="none"/>')
                    else: # Fallback
                        lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="blue" stroke-width="1" />')

        lines.append('</svg>')
        return "\n".join(lines)

def render_svg(graph: CircuitGraph, layout: Layout) -> str:
    return SVGRenderer(graph, layout).render()
