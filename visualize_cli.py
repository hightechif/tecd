from tecd import compile
from tecd.layout import compute_layout
from tecd.renderer import render_svg
import sys

def visualize(source_file, output_file):
    print(f"Reading {source_file}...")
    with open(source_file, 'r') as f:
        source = f.read()
    
    print("Compiling...")
    graph = compile(source)
    
    print("Layout...")
    layout = compute_layout(graph)
    
    print("Rendering...")
    svg = render_svg(graph, layout)
    
    with open(output_file, 'w') as f:
        f.write(svg)
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: uv run visualize_cli.py <input.tecd> <output.svg>")
    else:
        visualize(sys.argv[1], sys.argv[2])
