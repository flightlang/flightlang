from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Optional

@dataclass
class WaypointGrid:
    spacing: Any
    bearing: Any

def _num_to_str(n):
    if isinstance(n, dict) and 'value' in n:
        val = n['value']; unit = n.get('unit')
        return f"{val}{unit or ''}"
    return str(n)

class Runtime:
    def __init__(self):
        self.metadata = {}
        self.states: Dict[str, List[Tuple]] = {}
        self.current: Optional[str] = None

    def set_metadata(self, name: str, preflight: Optional[str], geofence: Optional[str]):
        self.metadata = {"name": name, "preflight": preflight, "geofence": geofence}

    def load_states(self, states: Dict[str, List[Tuple]]):
        self.states = states

    def set_start_state(self, name: str):
        if name not in self.states:
            raise ValueError(f"Unknown start state: {name}")
        self.current = name

    def _handle_action(self, name: str, args: List[Any], at_speed: Any, then_resume: bool):
        if name == 'climb_to':
            alt = _num_to_str(args[0]) if args else "<?>"
            speed = _num_to_str(at_speed) if at_speed else "default"
            print(f"[ACTION] Climb to {alt} at {speed}")
        elif name == 'goto':
            grid = args[0] if args else None
            spacing = getattr(grid,'spacing',None)
            bearing = getattr(grid,'bearing',None)
            print(f"[ACTION] Navigate grid: spacing={_num_to_str(spacing)}, bearing={_num_to_str(bearing)}")
        elif name == 'sidestep':
            dist = _num_to_str(args[0]) if args else "<?>"
            print(f"[ACTION] Sidestep {dist}")
            if then_resume:
                print("[ACTION] Resume previous path")
        elif name == 'return_to_launch':
            print("[ACTION] Return to Launch (RTL)")
        else:
            print(f"[ACTION] {name}({', '.join(_num_to_str(a) for a in args)})")

    def _state_tick(self, t_ms: int):
        for kind, *rest in self.states.get(self.current, []):
            if kind == 'deadline':
                ms = rest[0]
                print(f"[DEADLINE] {self.current} must complete step within {ms}ms")
        for kind, *rest in self.states.get(self.current, []):
            if kind == 'action':
                name, args, at_speed, then_resume = rest
                self._handle_action(name, args, at_speed, then_resume)

    def _try_transition(self, event_name: str):
        for kind, *rest in self.states.get(self.current, []):
            if kind == 'transition':
                event, target = rest
                if event == event_name:
                    print(f"[TRANSITION] {self.current} --{event}--> {target}")
                    self.current = target
                    return True
        return False

    def run(self, schedule: List[Tuple[int,str]]):
        print(f"=== Mission: {self.metadata.get('name')} ===")
        if self.metadata.get('preflight'):
            print(f"[PREFLIGHT] requires: {self.metadata['preflight']}")
        if self.metadata.get('geofence'):
            print(f"[GEOFENCE] keepout polygon: {self.metadata['geofence']}")
        print(f"[START] state: {self.current}")
        time_cursor = 0
        for t_ms, event in schedule:
            if t_ms > time_cursor:
                self._state_tick(t_ms)
                time_cursor = t_ms
            print(f"[EVENT @ {t_ms}ms] {event}")
            transitioned = self._try_transition(event)
            if transitioned:
                self._state_tick(t_ms)
        print("[END] schedule complete")
