# TECD

TECD is a text-first language for electrical circuits that compiles to IEC 60617 diagrams.

## Installation

```bash
uv sync
```

## Usage

```bash
uv run verify.py
```

---

# TECD Language Specification (v0.1)

*A PlantUML‑inspired, text‑first language for electrical circuits that compiles to IEC 60617 diagrams.*

---

## 1. Design Principles

TECD is designed to be:

* **Semantic** – users describe intent, not geometry
* **Declarative** – no drawing commands, only meaning
* **Pin‑safe** – electrical correctness is preserved
* **Deterministic** – the same input always produces the same output
* **Standard‑aware** – IEC 60617 is a constraint, not decoration

Diagrams are compiled artifacts. The text is the source of truth.

---

## 2. File Structure

Every circuit file follows this structure:

```
@circuit
  <component definitions>
  <connections>
  <options> (optional)
@end
```

The `@circuit` and `@end` keywords are mandatory.

---

## 3. Component Definitions

### Syntax

```
<TYPE> <NAME> ( <parameters> )
```

### Examples

```
VDC V1 (dc=5V)
RES R1 (value=1k)
CAP C1 (value=10uF)
IND L1 (value=10mH)
```

### Rules

* `TYPE` is uppercase and fixed
* `NAME` is user‑defined and unique
* Parameters are optional
* Parameter order does not matter

This section declares **what exists**, not how it is drawn.

---

## 4. Default Pin Model

Each component type has canonical pins.

| Component | Pins        |
| --------- | ----------- |
| RES       | left, right |
| CAP       | top, bottom |
| IND       | left, right |
| VDC       | +, −        |
| GND       | 0           |

If no pin is specified, defaults are used automatically.

---

## 5. Connections

### Core Operator

```
->
```

Represents a directed electrical connection.

---

### Linear Chains (PlantUML‑style)

```
V1 -> R1 -> C1 -> GND
```

Internally expands to:

```
V1.+ -> R1.left
R1.right -> C1.top
C1.bottom -> GND.0
```

This expansion is deterministic and invisible to the user.

---

### Branching with Nets

```
V1 -> R1 -> N1
N1 -> R2 -> GND
N1 -> C1 -> GND
```

### Net Rules

* Nets are implicit objects
* Nets have no parameters
* Nets represent electrical nodes

---

## 6. Explicit Pin Addressing

Used only when defaults are insufficient.

### Syntax

```
<Component>.<pin>
```

### Example

```
V1.+ -> R1.left
R1.right -> C1.top
```

Explicit pins always override defaults.

---

## 7. Ground Node

Ground is predefined and reserved.

```
GND
```

Or explicitly:

```
GND.0
```

Ground always maps to node `0`.

---

## 8. Parameters and Units

### Syntax

```
key=value
```

### Examples

```
R1 (value=10k tolerance=5%)
V1 (dc=12V)
C1 (value=100nF)
```

Rules:

* Units are required unless dimensionless
* Invalid or missing units are compilation errors

---

## 9. Options Block (Optional)

Used for rendering and compilation preferences.

```
@options
layout = horizontal
standard = IEC60617
@end
```

Options never affect circuit semantics.

---

## 10. Forbidden Constructs

The following are intentionally not allowed:

* Absolute coordinates
* Manual symbol placement
* Free‑form drawing commands
* Implicit shorts
* Ambiguous pin guessing

Ambiguity must result in a compiler error.

---

## 11. Minimal Complete Example

```
@circuit
VDC V1 (dc=5V)
RES R1 (value=1k)
CAP C1 (value=10uF)

V1 -> R1 -> C1 -> GND
@end
```

This file is:

* Human‑readable
* Machine‑parsable
* IEC‑compatible


---

## 12. Compilation Targets

From the same source file, TECD can generate:

* IEC 60617 electrical diagrams (SVG / Canvas)
* Netlists
* Linting and validation reports

---

## 13. Philosophy

TECD prioritizes correctness over creativity.

The language is strict by design.

Strict tools earn trust.
