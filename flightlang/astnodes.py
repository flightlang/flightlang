from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass
class LetDecl:
    name: str
    unit_type: str
    value_num: float
    value_unit: str

@dataclass
class Action:
    name: str
    args: List[Any]
    at_speed: Optional[Any] = None
    then_resume: bool = False

@dataclass
class Transition:
    event: str
    target_state: str

@dataclass
class Deadline:
    ms: int

@dataclass
class State:
    name: str
    items: List[Any] = field(default_factory=list)

@dataclass
class Preflight:
    condition: str

@dataclass
class Geofence:
    polygon_name: str

@dataclass
class Mission:
    name: str
    preflight: Optional[Preflight]
    geofence: Optional[Geofence]
    states: List[State]

@dataclass
class Program:
    lets: List[LetDecl]
    mission: Mission
