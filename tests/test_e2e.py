import pytest
from tecd import compile
from tecd.semantics import SemanticError

def compile_source(source):
    return compile(source)

def test_minimal_example():
    minimal = """
    @circuit
    VDC V1 (dc=5V)
    RES R1 (value=1k)
    CAP C1 (value=10uF)
    V1 -> R1 -> C1 -> GND
    @end
    """
    graph = compile_source(minimal)
    assert set(graph.components.keys()) == {"V1", "R1", "C1", "GND"}

def test_voltage_divider():
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
    graph = compile_source(vdiv)
    assert {"Vin", "R1", "R2", "GND", "Vout"}.issubset(graph.components.keys())
    assert graph.options["layout"] == "vertical"

def test_all_new_symbols():
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
    graph = compile_source(all_syms)
    expected = {"V1", "S1", "D1", "L1", "I1", "GND"}
    assert expected.issubset(graph.components.keys())

def test_rlc_circuit():
    rlc = """
    @circuit
    VAC Source (ac=12V)
    RES R1 (value=100R)
    IND L1 (value=10mH)
    CAP C1 (value=10uF)
    Source -> R1 -> L1 -> C1 -> GND
    @end
    """
    graph = compile_source(rlc)
    assert {"Source", "R1", "L1", "C1", "GND"}.issubset(graph.components.keys())

def test_bridge_rectifier():
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
    graph = compile_source(rect)
    expected = {"AC_In", "D1", "D2", "D3", "D4", "Load", "CFilter", "GND", "Top", "Bottom"}
    assert expected.issubset(graph.components.keys())

def test_wheatstone_bridge():
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
    graph = compile_source(wbridge)
    expected = {"Vs", "R1", "R2", "R3", "R4", "Rg", "GND"}
    assert expected.issubset(graph.components.keys())

def test_duplicate_name_error():
    dup_name = """
    @circuit
    RES R1 (v=1)
    CAP R1 (v=2)
    @end
    """
    with pytest.raises(Exception): # Ideally SemanticError, but verify.py catches Exception
        compile_source(dup_name)

def test_invalid_syntax():
    invalid_syn = """
    @circuit
    RES R1 (val=1)
    R1 -/> GND
    @end
    """
    with pytest.raises(Exception):
        compile_source(invalid_syn)

def test_transistors():
    trans = """
    @circuit
    VDC Vcc (v=5V)
    NPN Q1 (model=2N3904)
    NMOS M1 (model=IRF540)
    NOT Inv1
    AND And1
    Q1.B -> Q1.C
    @end
    """
    graph = compile_source(trans)
    assert {"Vcc", "Q1", "M1", "Inv1", "And1"}.issubset(graph.components.keys())

def test_unknown_component_type():
    unknown_type = """
    @circuit
    FOO Bar (p=1)
    @end
    """
    # This scenario is tricky as per verify.py comments, but it should fail
    # likely at parser unexpected token LPAREN or earlier
    with pytest.raises(Exception):
        compile_source(unknown_type)
