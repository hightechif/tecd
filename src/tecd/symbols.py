from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass
class Symbol:
    path: str
    width: float
    height: float
    pins: Dict[str, Tuple[float, float]] # pin_name -> (x, y)
    label_offset: Tuple[float, float] = (0, -25)

# Coordinate system: Center is (0,0) usually, or consistent origin.
# Let's use components centered at (0,0) for easiest rotation/placement.
# Standard grid unit = 10px? Let's say 20px per pin distance.

# IEC 60617 Resistor: Rectangle
# Dimensions: 40x10 ?
RESISTOR = Symbol(
    path='<rect x="-20" y="-8" width="40" height="16" fill="none" stroke="currentColor" stroke-width="2"/>',
    width=40,
    height=16,
    pins={
        'left': (-20, 0),
        'right': (20, 0)
    },
    label_offset=(0, -25)
)

# IEC Capacitor: Two parallel plates
CAPACITOR = Symbol(
    path='''
        <line x1="-5" y1="-15" x2="-5" y2="15" stroke="currentColor" stroke-width="2"/>
        <line x1="5" y1="-15" x2="5" y2="15" stroke="currentColor" stroke-width="2"/>
        <line x1="-20" y1="0" x2="-5" y2="0" stroke="currentColor" stroke-width="2"/>
        <line x1="5" y1="0" x2="20" y2="0" stroke="currentColor" stroke-width="2"/>
    ''',
    width=40,
    height=30,
    pins={
        'left': (-20, 0), # Mapped from top/bottom? Needs rotation logic or standardization.
        'right': (20, 0), # Standardize on Horizontal by default?
        # If user uses "top/bottom" pins, we might need vertical orientation by default?
        # But for now let's define horizontally aligned defaults for "flow".
        'top': (-20, 0), # Alias for Layout flow
        'bottom': (20, 0)
    }
)

# IEC Inductor: 4 semicircles
INDUCTOR = Symbol(
    path='''
        <path d="M -20 0 Q -15 -10 -10 0 T 0 0 T 10 0 T 20 0" fill="none" stroke="currentColor" stroke-width="2"/>
    ''',
    width=40,
    height=10,
    pins={
        'left': (-20, 0),
        'right': (20, 0)
    }
)

# VDC: DC Voltage Source (Circle with + - or Battery lines)
# IEC Battery: Long line (+), Short line thick (-)
VDC = Symbol(
    path='''
        <line x1="-5" y1="-10" x2="-5" y2="10" stroke="currentColor" stroke-width="2"/>
        <line x1="5" y1="-5" x2="5" y2="5" stroke="currentColor" stroke-width="4"/>
        <line x1="-20" y1="0" x2="-5" y2="0" stroke="currentColor" stroke-width="2"/>
        <line x1="5" y1="0" x2="20" y2="0" stroke="currentColor" stroke-width="2"/>
        <text x="-10" y="-15" font-size="10" fill="currentColor">+</text>
    ''',
    width=40,
    height=20,
    pins={
        '+': (-20, 0),
        '-': (20, 0),
        'left': (-20, 0), # Aliases
        'right': (20, 0)
    }
)

# GND: Bar
GND = Symbol(
    path='''
        <line x1="-15" y1="0" x2="15" y2="0" stroke="currentColor" stroke-width="2"/>
        <line x1="0" y1="-10" x2="0" y2="0" stroke="currentColor" stroke-width="2"/>
    ''',
    width=30,
    height=20,
    pins={
        '0': (0, -10),
        'top': (0, -10)
    },
    label_offset=(0, 25)
)

# Diode: Triangle -> Bar
DIODE = Symbol(
    path='''
        <polygon points="-10,-10 -10,10 10,0" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="10" y1="-10" x2="10" y2="10" stroke="currentColor" stroke-width="2"/>
        <line x1="-20" y1="0" x2="-10" y2="0" stroke="currentColor" stroke-width="2"/>
        <line x1="10" y1="0" x2="20" y2="0" stroke="currentColor" stroke-width="2"/>
    ''',
    width=40,
    height=20,
    pins={
        'anode': (-20, 0),
        'cathode': (20, 0),
        'left': (-20, 0),
        'right': (20, 0)
    },
     label_offset=(0, -25)
)

# LED: Diode + Arrows
LED = Symbol(
    path='''
        <polygon points="-10,-10 -10,10 10,0" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="10" y1="-10" x2="10" y2="10" stroke="currentColor" stroke-width="2"/>
        <line x1="-20" y1="0" x2="-10" y2="0" stroke="currentColor" stroke-width="2"/>
        <line x1="10" y1="0" x2="20" y2="0" stroke="currentColor" stroke-width="2"/>
        <line x1="-5" y1="-12" x2="5" y2="-22" stroke="currentColor" stroke-width="1"/>
        <polygon points="5,-22 2,-18 0,-21" fill="currentColor"/>
        <line x1="0" y1="-12" x2="10" y2="-22" stroke="currentColor" stroke-width="1"/>
        <polygon points="10,-22 7,-18 5,-21" fill="currentColor"/>
    ''',
    width=40,
    height=30,
    pins={
        'anode': (-20, 0),
        'cathode': (20, 0),
        'left': (-20, 0),
        'right': (20, 0)
    },
    label_offset=(0, -35)
)

# Switch: SPST
SWITCH = Symbol(
    path='''
        <line x1="-20" y1="0" x2="-10" y2="0" stroke="currentColor" stroke-width="2"/>
        <line x1="10" y1="0" x2="20" y2="0" stroke="currentColor" stroke-width="2"/>
        <circle cx="-10" cy="0" r="2" fill="none" stroke="currentColor" stroke-width="2"/>
        <circle cx="10" cy="0" r="2" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="-10" y1="0" x2="8" y2="-10" stroke="currentColor" stroke-width="2"/>
    ''',
    width=40,
    height=20,
    pins={
        '1': (-20, 0),
        '2': (20, 0),
        'left': (-20, 0),
        'right': (20, 0)
    },
    label_offset=(0, -25)
)

# VAC: AC Voltage Source (Circle with sine)
VAC = Symbol(
    path='''
        <circle cx="0" cy="0" r="15" fill="none" stroke="currentColor" stroke-width="2"/>
        <path d="M -8 0 Q -4 -8 0 0 T 8 0" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="-20" y1="0" x2="-15" y2="0" stroke="currentColor" stroke-width="2"/>
        <line x1="15" y1="0" x2="20" y2="0" stroke="currentColor" stroke-width="2"/>
    ''',
    width=40,
    height=30,
    pins={
        '+': (-20, 0),
        '-': (20, 0),
        'left': (-20, 0),
        'right': (20, 0)
    },
    label_offset=(0, -25)
)

# IDC: Current Source (Circle with arrow)
IDC = Symbol(
    path='''
        <circle cx="0" cy="0" r="15" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="-10" y1="0" x2="10" y2="0" stroke="currentColor" stroke-width="2"/>
        <polygon points="10,0 4,-4 4,4" fill="currentColor"/>
        <line x1="-20" y1="0" x2="-15" y2="0" stroke="currentColor" stroke-width="2"/>
        <line x1="15" y1="0" x2="20" y2="0" stroke="currentColor" stroke-width="2"/>
    ''',
    width=40,
    height=30,
    pins={
        '+': (-20, 0),
        '-': (20, 0),
        'left': (-20, 0),
        'right': (20, 0)
    },
    label_offset=(0, -25)
)

# Transistors
NPN = Symbol(
    path='''
        <circle cx="0" cy="0" r="20" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="-10" y1="-12" x2="-10" y2="12" stroke="currentColor" stroke-width="2"/>
        <line x1="-20" y1="0" x2="-10" y2="0" stroke="currentColor" stroke-width="2"/>
        <line x1="-10" y1="-7" x2="10" y2="-15" stroke="currentColor" stroke-width="2"/>
        <line x1="-10" y1="7" x2="10" y2="15" stroke="currentColor" stroke-width="2"/>
        <line x1="10" y1="-15" x2="20" y2="-15" stroke="currentColor" stroke-width="2"/>
        <line x1="10" y1="15" x2="20" y2="15" stroke="currentColor" stroke-width="2"/>
        <polygon points="10,15 6,8 3,11" fill="currentColor"/>
    ''',
    width=40,
    height=40,
    pins={'B': (-20, 0), 'C': (20, -15), 'E': (20, 15)},
    label_offset=(0, -30)
)

PNP = Symbol(
    path='''
        <circle cx="0" cy="0" r="20" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="-10" y1="-12" x2="-10" y2="12" stroke="currentColor" stroke-width="2"/>
        <line x1="-20" y1="0" x2="-10" y2="0" stroke="currentColor" stroke-width="2"/>
        <line x1="-10" y1="-7" x2="10" y2="-15" stroke="currentColor" stroke-width="2"/>
        <line x1="-10" y1="7" x2="10" y2="15" stroke="currentColor" stroke-width="2"/>
        <line x1="10" y1="-15" x2="20" y2="-15" stroke="currentColor" stroke-width="2"/>
        <line x1="10" y1="15" x2="20" y2="15" stroke="currentColor" stroke-width="2"/>
        <polygon points="-5,9 -1,2 -8,2" fill="currentColor"/>
    ''',
    width=40,
    height=40,
    pins={'B': (-20, 0), 'C': (20, -15), 'E': (20, 15)},
    label_offset=(0, -30)
)

NMOS = Symbol(
    path='''
        <circle cx="0" cy="0" r="20" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="-10" y1="-12" x2="-10" y2="12" stroke="currentColor" stroke-width="2"/>
        <line x1="-15" y1="-12" x2="-15" y2="12" stroke="currentColor" stroke-width="2"/>
        <line x1="-20" y1="0" x2="-15" y2="0" stroke="currentColor" stroke-width="2"/>
        <line x1="-10" y1="-10" x2="0" y2="-10" stroke="currentColor" stroke-width="2"/>
        <line x1="0" y1="-10" x2="0" y2="-15" stroke="currentColor" stroke-width="2"/>
        <line x1="0" y1="-15" x2="20" y2="-15" stroke="currentColor" stroke-width="2"/>
        <line x1="-10" y1="10" x2="0" y2="10" stroke="currentColor" stroke-width="2"/>
        <line x1="0" y1="10" x2="0" y2="15" stroke="currentColor" stroke-width="2"/>
        <line x1="0" y1="15" x2="20" y2="15" stroke="currentColor" stroke-width="2"/>
        <line x1="-10" y1="0" x2="0" y2="0" stroke="currentColor" stroke-width="2"/>
        <polygon points="-10,0 -4,-3 -4,3" fill="currentColor"/>
    ''',
    width=40,
    height=40,
    pins={'G': (-20, 0), 'D': (20, -15), 'S': (20, 15)},
    label_offset=(0, -30)
)

# Logic Gates
AND = Symbol(
    path='''
        <path d="M -10 -15 V 15 A 15 15 0 0 0 10 15 V -15 A 15 15 0 0 0 -10 -15 Z" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="-10" y1="-15" x2="5" y2="-15" stroke="currentColor" stroke-width="2"/> 
        <line x1="-10" y1="15" x2="5" y2="15" stroke="currentColor" stroke-width="2"/>
        <path d="M 5 -15 A 15 15 0 0 1 5 15" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="-10" y1="-15" x2="-10" y2="15" stroke="currentColor" stroke-width="2"/>
        <line x1="20" y1="0" x2="30" y2="0" stroke="currentColor" stroke-width="2"/>
        <line x1="-20" y1="-5" x2="-10" y2="-5" stroke="currentColor" stroke-width="2"/>
        <line x1="-20" y1="5" x2="-10" y2="5" stroke="currentColor" stroke-width="2"/>
    ''',
    # Simplified Path
    # Actually standard AND shape is flat back, curved front.
   # Left x=-10. Top y=-15, Bottom y=15. Center of arc at x=5?
    # Let's simple path
    width=50,
    height=40,
    pins={'in1': (-20, -5), 'in2': (-20, 5), 'out': (30, 0)},
    label_offset=(0, -25)
)

OR = Symbol(
    path='''
        <path d="M -15 -15 Q 5 -15 15 0 Q 5 15 -15 15 Q -5 0 -15 -15" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="15" y1="0" x2="25" y2="0" stroke="currentColor" stroke-width="2"/>
        <line x1="-25" y1="-5" x2="-10" y2="-5" stroke="currentColor" stroke-width="2"/>
        <line x1="-25" y1="5" x2="-10" y2="5" stroke="currentColor" stroke-width="2"/>
    ''',
    width=50,
    height=40,
    pins={'in1': (-25, -5), 'in2': (-25, 5), 'out': (25, 0)},
    label_offset=(0, -25)
)

NOT = Symbol(
    path='''
        <polygon points="-10,-10 -10,10 10,0" fill="none" stroke="currentColor" stroke-width="2"/>
        <circle cx="13" cy="0" r="3" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="-20" y1="0" x2="-10" y2="0" stroke="currentColor" stroke-width="2"/>
        <line x1="16" y1="0" x2="26" y2="0" stroke="currentColor" stroke-width="2"/>
    ''',
    width=46,
    height=20,
    pins={'in': (-20, 0), 'out': (26, 0)},
    label_offset=(0, -20)
)

NAND = Symbol(
    path='''
        <path d="M -10 -15 V 15" stroke="currentColor" stroke-width="2"/>
        <path d="M -10 -15 H 5 A 15 15 0 0 1 5 15 H -10" fill="none" stroke="currentColor" stroke-width="2"/>
        <circle cx="23" cy="0" r="3" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="26" y1="0" x2="36" y2="0" stroke="currentColor" stroke-width="2"/>
        <line x1="-20" y1="-5" x2="-10" y2="-5" stroke="currentColor" stroke-width="2"/>
        <line x1="-20" y1="5" x2="-10" y2="5" stroke="currentColor" stroke-width="2"/>
    ''',
    width=56,
    height=40,
    pins={'in1': (-20, -5), 'in2': (-20, 5), 'out': (36, 0)},
    label_offset=(0, -25)
)

SYMBOL_MAP = {
    'RES': RESISTOR,
    'CAP': CAPACITOR,
    'IND': INDUCTOR,
    'VDC': VDC,
    'GND': GND,
    'DIODE': DIODE,
    'LED': LED,
    'SWITCH': SWITCH,
    'VAC': VAC,
    'IDC': IDC,
    'NPN': NPN,
    'PNP': PNP,
    'NMOS': NMOS,
    # 'PMOS': PMOS, # reuse NMOS with varied path or create new
    'AND': AND,
    'OR': OR,
    'NOT': NOT,
    'NAND': NAND,
    'JUNCTION': Symbol(path='<circle r="3" fill="currentColor"/>', width=6, height=6, pins={'0':(0,0)})
}

def get_symbol(type_name: str) -> Symbol:
    return SYMBOL_MAP.get(type_name, SYMBOL_MAP['RES']) # Fallback to box
