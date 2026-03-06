import re
from typing import List

TOKEN_SPEC = [
    ("COMMENT",   r"//[^\n]*"),
    ("SKIP",      r"[ \t\r]+"),
    ("NEWLINE",   r"\n"),
    ("ARROW",     r"->"),
    ("AT",        r"@"),
    ("COMMA",     r","),
    ("COLON",     r":"),
    ("LPAREN",    r"\("),
    ("RPAREN",    r"\)"),
    ("LBRACE",    r"\{"),
    ("RBRACE",    r"\}"),
    ("EQ",        r"="),
    ("STRING",    r"\"([^\"\\]|\\.)*\""),
    ("NUMBER",    r"\d+(?:\.\d+)?"),
    ("IDENT",     r"[A-Za-z_][A-Za-z0-9_]*"),
]

KEYWORDS = {
    "let","mission","state","on","action","deadline",
    "preflight","requires","geofence","keepout","polygon",
    "then","resume",
}

class Token:
    __slots__ = ("type","value","line","col")
    def __init__(self, typ, value, line, col):
        self.type = typ; self.value = value; self.line = line; self.col = col
    def __repr__(self):
        return f"Token({self.type},{self.value!r},{self.line}:{self.col})"

class Lexer:
    def __init__(self, src: str):
        self.src = src
        self.regex = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC))
        self.line = 1; self.col = 1; self.pos = 0

    def tokenize(self) -> List['Token']:
        tokens: List[Token] = []
        while self.pos < len(self.src):
            m = self.regex.match(self.src, self.pos)
            if not m:
                end = self.src.find("\n", self.pos)
                if end == -1: end = len(self.src)
                snippet = self.src[self.pos:end]
                raise SyntaxError(f"Unexpected character at {self.line}:{self.col}: {snippet!r}")
            typ = m.lastgroup; text = m.group(typ)
            if typ == "NEWLINE":
                self.line += 1; self.col = 1; self.pos = m.end(); continue
            if typ in ("SKIP","COMMENT"):
                self._advance(m); continue
            if typ == "IDENT" and text in KEYWORDS:
                tokens.append(Token(text.upper(), text, self.line, self.col))
            elif typ == "STRING":
                val = bytes(text[1:-1], "utf-8").decode("unicode_escape")
                tokens.append(Token("STRING", val, self.line, self.col))
            else:
                tokens.append(Token(typ, text, self.line, self.col))
            self._advance(m)
        tokens.append(Token("EOF","",self.line,self.col))
        return tokens

    def _advance(self, m):
        span = m.end() - self.pos
        self.col += span; self.pos = m.end()
