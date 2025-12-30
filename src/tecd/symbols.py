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
    'JUNCTION': Symbol(path='<circle r="3" fill="currentColor"/>', width=6, height=6, pins={'0':(0,0)})
}

def get_symbol(type_name: str) -> Symbol:
    return SYMBOL_MAP.get(type_name, SYMBOL_MAP['RES']) # Fallback to box
