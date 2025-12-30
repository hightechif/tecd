from . import compile
from .layout import compute_layout
from .renderer import render_svg
import sys
import os
import time
import argparse

def visualize(source_file, output_file, layout_override=None):
    print(f"Reading {source_file}...")
    try:
        with open(source_file, 'r') as f:
            source = f.read()
        
        print("Compiling...")
        graph = compile(source)
        
        if layout_override:
            print(f"Overriding layout to: {layout_override}")
            graph.options['layout'] = layout_override
        
        print("Layout...")
        layout = compute_layout(graph)
        
        print("Rendering...")
        svg = render_svg(graph, layout)
        
        with open(output_file, 'w') as f:
            f.write(svg)
        print(f"Saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def watch_mode(source_file, output_file, layout_override=None):
    print(f"Watching {source_file} for changes...")
    last_mtime = 0
    try:
        while True:
            try:
                mtime = os.path.getmtime(source_file)
            except FileNotFoundError:
                print(f"File not found: {os.path.abspath(source_file)}")
                time.sleep(1)
                continue

            if mtime > last_mtime:
                print("\n--- Change detected ---")
                visualize(source_file, output_file, layout_override)
                last_mtime = mtime
            
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping watch mode.")

def main():
    parser = argparse.ArgumentParser(description="TECD: Text to Electrical Circuit Diagram Visualizer")
    parser.add_argument("input", help="Input .tecd file")
    parser.add_argument("output", nargs="?", help="Output .svg file")
    parser.add_argument("--layout", "-l", choices=['horizontal', 'vertical', 'automatic'], help="Override layout direction")
    parser.add_argument("--watch", "-w", action="store_true", help="Watch input file for changes and re-render")

    args = parser.parse_args()
    
    source = args.input
    output = args.output
    
    if not output:
        base, _ = os.path.splitext(source)
        output = base + ".svg"
        
    print(f"Input: {source}")
    print(f"Output: {output}")

    if args.watch:
        watch_mode(source, output, args.layout)
    else:
        visualize(source, output, args.layout)

if __name__ == "__main__":
    main()
