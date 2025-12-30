# TECD Examples

This directory contains example circuit definitions (`.tecd` files) demonstrating the features of the TECD language.

## Basic Examples
- **[rectifier.tecd](rectifier.tecd)**: A simple Diode Bridge Rectifier using basic components.
- **[voltage_divider.tecd](voltage_divider.tecd)**: Minimal two-resistor divider.
- **[rc_filter.tecd](rc_filter.tecd)**: Basic passive filter.
- **[rlc_series.tecd](rlc_series.tecd)**: Series RLC circuit.

## Advanced Examples
- **[wheatstone_bridge.tecd](wheatstone_bridge.tecd)**: Demonstrates structured `horizontal` layout and bridge connections.
- **[transistors.tecd](transistors.tecd)**: Showcases active components (NPN, NMOS) and Logic Gates (AND, OR, NOT).
- **[all_symbols.tecd](all_symbols.tecd)**: A reference file containing all available symbols.

## How to Run
To visualize an example, run:

```bash
uv run tecd examples/rectifier.tecd output.svg
```
