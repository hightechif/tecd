import sys
import os
import traceback

# Add src to path
sys.path.insert(0, os.path.abspath('src'))

from tecd import compile
from tecd.semantics import SemanticError

def run_test(name, source, expected_components=None, should_fail=False):
    print(f"Testing: {name}...", end=" ")
    try:
        graph = compile(source)
        if should_fail:
            print("FAILED (Expected failure but succeeded)")
            return False
            
        # Verify components
        if expected_components:
            found_comps = set(graph.components.keys())
            # Filter out implicit stuff if needed, but for now exact match
            # If implicit GND or JUNCTION is added, we might need loose check
            # For now, let's check if expected is a subset
            missing = set(expected_components) - found_comps
            if missing:
                print(f"FAILED (Missing components: {missing})")
                return False
        
        print("PASSED")
        return True
        
    except Exception as e:
        if should_fail:
            # We could check the error message too
            print(f"PASSED (Caught expected error: {type(e).__name__})")
            return True
        else:
            print(f"FAILED (Error: {e})")
            # traceback.print_exc()
            return False

def main():
    print("=== TECD Verification Suite ===\n")
    
    # 1. Minimal Example
    minimal = """
    @circuit
    VDC V1 (dc=5V)
    RES R1 (value=1k)
    CAP C1 (value=10uF)
    V1 -> R1 -> C1 -> GND
    @end
    """
    run_test("Minimal Complete Example", minimal, ["V1", "R1", "C1", "GND"])

    # 2. Voltage Divider (Vertical Layout Test)
    vdiv = """
    @circuit
    @options
      layout = vertical
    @end
    VDC Vin (dc=12V)
    RES R1 (value=10k)
    RES R2 (value=2.2k)
    Vin -> R1 -> Vout
    Vout -> R2 -> GND
    @end
    """
    run_test("Voltage Divider", vdiv, ["Vin", "R1", "R2", "GND", "Vout"])

    # 3. New Symbols Test
    new_sym = """
    @circuit
    VAC V1 (ac=220V)
    SWITCH S1 (type=spst)
    DIODE D1 (model=1N4007)
    IED L1 (color=red)  
    IDC I1 (current=1A)
    V1 -> S1 -> D1 -> I1 -> GND
    @end
    """
    # Note: IED is typo for LED, should fail parser if strict or pass as generic if lenient? 
    # Parser: parse_component expects TYPE ID. If IED is not a known type in Lexer?
    # Lexer recognizes known types. If unknown, it parses as ID.
    # Parser `parse_component` expects: `TYPE` token then `ID`.
    # If `IED` is lexed as `ID` (not `TYPE`), then `parse_statement` sees `ID` and calls `parse_connection_chain`.
    # `IED L1 ...` -> `IED` is ID. `L1` is ID.
    # `IED L1` looks like a connection chain `IED -> L1`? No arrow.
    # `parse_connection_chain`: `parse_pin_reference` (IED) ... then expects ARROW.
    # If no arrow, it consumes IED. Then loop finishes.
    # Then next token `L1`...
    # This might actually fail or parse weirdly. Let's see.
    # Let's fix the test case to use valid LED first.
    
    all_syms = """
    @circuit
    VAC V1 (ac=220V)
    SWITCH S1 (type=spst)
    DIODE D1 (model=1N4007)
    LED L1 (color=red)
    IDC I1 (current=1A)
    V1 -> S1 -> D1 -> L1 -> I1 -> GND
    @end
    """
    run_test("All New Symbols", all_syms, ["V1", "S1", "D1", "L1", "I1", "GND"])

    # 4. RLC Circuit
    rlc = """
    @circuit
    VAC Source (ac=12V)
    RES R1 (value=100R)
    IND L1 (value=10mH)
    CAP C1 (value=10uF)
    Source -> R1 -> L1 -> C1 -> GND
    @end
    """
    run_test("RLC Circuit", rlc, ["Source", "R1", "L1", "C1", "GND"])

    # 5. Bridge Rectifier
    rect = """
    @circuit
    VAC AC_In (v=24V)
    DIODE D1 (model=1N4007)
    DIODE D2 (model=1N4007)
    DIODE D3 (model=1N4007)
    DIODE D4 (model=1N4007)
    RES Load (v=1k)
    CAP CFilter (v=100uF)

    AC_In.+ -> D1 -> Top
    AC_In.+ -> D2 -> Bottom
    AC_In.- -> D3 -> Top
    AC_In.- -> D4 -> Bottom

    Top -> Load -> Bottom
    Top -> CFilter -> Bottom

    Bottom -> GND
    @end
    """
    run_test("Bridge Rectifier", rect, ["AC_In", "D1", "D2", "D3", "D4", "Load", "CFilter", "GND", "Top", "Bottom"])

    # 6. Wheatstone Bridge
    wbridge = """
    @circuit
    VDC Vs (v=10V)
    RES R1 (v=1k)
    RES R2 (v=1k)
    RES R3 (v=1k)
    RES R4 (v=1k)
    RES Rg (v=50R)
    
    Vs.+ -> Top
    Vs.- -> GND
    
    Top -> R1 -> Left
    Top -> R3 -> Right
    
    Left -> R2 -> Bottom
    Right -> R4 -> Bottom
    
    Left -> Rg -> Right
    
    Bottom -> GND
    @end
    """
    run_test("Wheatstone Bridge", wbridge, ["Vs", "R1", "R2", "R3", "R4", "Rg", "GND"])

    # 7. Duplicate Name Error
    dup_name = """
    @circuit
    RES R1 (v=1)
    CAP R1 (v=2)
    @end
    """
    run_test("Duplicate Name Error", dup_name, should_fail=True)

    # 5. Invalid Token/Syntax
    invalid_syn = """
    @circuit
    RES R1 (val=1)
    R1 -/> GND
    @end
    """
    run_test("Invalid Syntax", invalid_syn, should_fail=True)

    # 6. Unknown Component Type (Lexer should see ID, parser tries connection)
    # If I write: "FOO Bar (p=1)"
    # Lexer: FOO (ID), Bar (ID), LPAREN...
    # Parser: "FOO" -> parse_connection_chain -> parse_pin_reference(FOO). No arrow. Done.
    # Next: "Bar" -> parse_connection_chain -> parse_pin_reference(Bar). No arrow. Done.
    # Next: LPAREN. parse_statement -> Unexpected token LPAREN.
    unknown_type = """
    @circuit
    FOO Bar (p=1)
    @end
    """
    run_test("Unknown Component Type", unknown_type, should_fail=True)
    
if __name__ == "__main__":
    main()
