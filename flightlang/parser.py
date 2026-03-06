from __future__ import annotations
from typing import List, Any, Optional
from .lexer import Lexer, Token
from . import astnodes as A

class Parser:
    def __init__(self, src: str):
        self.tokens: List[Token] = Lexer(src).tokenize()
        self.i = 0

    def _cur(self) -> Token:
        return self.tokens[self.i]

    def _eat(self, typ: str) -> Token:
        t = self._cur()
        if t.type != typ:
            raise SyntaxError(f"Expected {typ} at {t.line}:{t.col}, got {t.type}")
        self.i += 1
        return t

    def _match(self, typ: str) -> Optional[Token]:
        if self._cur().type == typ:
            t = self._cur(); self.i += 1; return t
        return None

    def parse(self) -> A.Program:
        lets: List[A.LetDecl] = []
        while self._cur().type == "LET":
            lets.append(self.parse_let())
        mission = self.parse_mission()
        self._eat("EOF")
        return A.Program(lets=lets, mission=mission)

    def parse_let(self) -> A.LetDecl:
        self._eat("LET")
        name = self._eat("IDENT").value
        self._eat("COLON")
        unit_type = self._eat("IDENT").value
        self._eat("EQ")
        num = float(self._eat("NUMBER").value)
        unit_tok = self._match("IDENT")
        value_unit = unit_tok.value if unit_tok else unit_type
        return A.LetDecl(name=name, unit_type=unit_type, value_num=num, value_unit=value_unit)

    def parse_mission(self) -> A.Mission:
        self._eat("MISSION")
        name = self._eat("IDENT").value
        self._eat("LBRACE")
        preflight = None; geofence = None; states: List[A.State] = []
        while self._cur().type != "RBRACE":
            if self._cur().type == "PREFLIGHT":
                preflight = self.parse_preflight()
            elif self._cur().type == "GEOFENCE":
                geofence = self.parse_geofence()
            elif self._cur().type == "STATE":
                states.append(self.parse_state())
            else:
                t = self._cur(); raise SyntaxError(f"Unexpected token {t.type} at {t.line}:{t.col}")
        self._eat("RBRACE")
        return A.Mission(name=name, preflight=preflight, geofence=geofence, states=states)

    def parse_preflight(self) -> A.Preflight:
        self._eat("PREFLIGHT"); self._eat("REQUIRES")
        parts = []
        while self._cur().type not in ("STATE","GEOFENCE","RBRACE"):
            if self._cur().type in ("PREFLIGHT",): break
            tok = self._cur(); val = tok.value
            if tok.type == "STRING": val = f'"{val}"'
            parts.append(val); self.i += 1
        return A.Preflight(condition=" ".join(parts).strip())

    def parse_geofence(self) -> A.Geofence:
        self._eat("GEOFENCE"); self._eat("KEEPOUT"); self._eat("POLYGON")
        name = self._eat("STRING").value
        return A.Geofence(polygon_name=name)

    def parse_state(self) -> A.State:
        self._eat("STATE"); name = self._eat("IDENT").value; self._eat("LBRACE")
        items: List[Any] = []
        while self._cur().type != "RBRACE":
            tok = self._cur()
            if tok.type == "ON": items.append(self.parse_transition())
            elif tok.type == "ACTION": items.append(self.parse_action())
            elif tok.type == "DEADLINE": items.append(self.parse_deadline())
            else: raise SyntaxError(f"Unexpected token {tok.type} in state at {tok.line}:{tok.col}")
        self._eat("RBRACE")
        return A.State(name=name, items=items)

    def parse_transition(self) -> A.Transition:
        self._eat("ON"); event = self._eat("IDENT").value; self._eat("ARROW"); target = self._eat("IDENT").value
        return A.Transition(event=event, target_state=target)

    def parse_action(self) -> A.Action:
        self._eat("ACTION"); name = self._eat("IDENT").value; self._eat("LPAREN")
        args: List[Any] = []
        if self._cur().type != "RPAREN":
            args.append(self.parse_expr())
            while self._match("COMMA"): args.append(self.parse_expr())
        self._eat("RPAREN")
        at_speed = None; then_resume = False
        if self._match("AT"): at_speed = self.parse_expr()
        if self._match("THEN"): self._eat("RESUME"); then_resume = True
        return A.Action(name=name, args=args, at_speed=at_speed, then_resume=then_resume)

    def parse_deadline(self) -> A.Deadline:
        self._eat("DEADLINE"); ms = int(float(self._eat("NUMBER").value))
        if self._cur().type == "IDENT" and self._cur().value == "ms": self.i += 1
        return A.Deadline(ms=ms)

    def parse_expr(self) -> Any:
        tok = self._cur()
        if tok.type == "NUMBER":
            num = float(self._eat("NUMBER").value); unit = None
            if self._cur().type == "IDENT" and self._cur().value in ("m","mps","deg","ms"):
                unit = self._eat("IDENT").value
            return {"kind":"number","value":num,"unit":unit}
        if tok.type == "STRING":
            return {"kind":"string","value":self._eat("STRING").value}
        if tok.type == "IDENT":
            ident = self._eat("IDENT").value
            if self._match("LPAREN"):
                kwargs = {}
                if self._cur().type != "RPAREN":
                    key = self._eat("IDENT").value; self._eat("COLON"); val = self.parse_expr(); kwargs[key] = val
                    while self._match("COMMA"):
                        key = self._eat("IDENT").value; self._eat("COLON"); val = self.parse_expr(); kwargs[key] = val
                self._eat("RPAREN")
                return {"kind":"call","name":ident,"kwargs":kwargs}
            else:
                return {"kind":"ident","name":ident}
        raise SyntaxError(f"Unexpected expression token {tok.type} at {tok.line}:{tok.col}")
