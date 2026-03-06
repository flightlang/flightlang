from __future__ import annotations
from . import astnodes as A

VALID_UNITS = {"m","mps","deg","ms"}

def typecheck(prog: A.Program) -> None:
    for let in prog.lets:
        if let.unit_type not in VALID_UNITS:
            raise TypeError(f"Unknown unit type for '{let.name}': {let.unit_type}")
        if let.value_unit not in VALID_UNITS:
            raise TypeError(f"Unknown unit for '{let.name}': {let.value_unit}")
