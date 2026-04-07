"""
parse_tree.py — estructuras compartidas para análisis sintáctico
Compiladores — Entrega 2 | Lenguaje fuente → TypeScript
"""

from dataclasses import dataclass, field
from typing import List, Optional

from tokens import Token


@dataclass
class SyntaxErrorInfo:
    """Error sintáctico con posición precisa y contexto."""

    mensaje: str
    fila: int
    columna: int
    esperado: List[str] = field(default_factory=list)
    recibido: str = ""
    sugerencia: str = ""

    def __str__(self) -> str:
        extras = []
        if self.esperado:
            extras.append("esperado: " + ", ".join(self.esperado))
        if self.recibido:
            extras.append(f"recibido: {self.recibido}")
        if self.sugerencia:
            extras.append(f"sugerencia: {self.sugerencia}")
        sufijo = f" ({'; '.join(extras)})" if extras else ""
        return f"Fila {self.fila}, columna {self.columna}: {self.mensaje}{sufijo}"


class ParserAbort(Exception):
    """Excepción interna para cortar el análisis al primer error."""

    def __init__(self, error: SyntaxErrorInfo):
        self.error = error
        super().__init__(str(error))


@dataclass
class ParseNode:
    """Nodo genérico del árbol de análisis sintáctico."""

    symbol: str
    children: List["ParseNode"] = field(default_factory=list)
    token: Optional[Token] = None
    is_terminal: bool = False

    def add_child(self, child: "ParseNode") -> None:
        self.children.append(child)

    @property
    def label(self) -> str:
        if self.token is None:
            return self.symbol
        lexema = self.token.lexema if self.token.lexema else self.token.tipo.name
        return f"{self.symbol} [{lexema}]"

    def to_ascii(self) -> str:
        """Devuelve una representación ASCII legible del árbol."""
        lines = [self.label]
        for index, child in enumerate(self.children):
            is_last = index == len(self.children) - 1
            lines.extend(child._to_ascii_lines("", is_last))
        return "\n".join(lines)

    def _to_ascii_lines(self, prefix: str, is_last: bool) -> List[str]:
        connector = "└── " if is_last else "├── "
        lines = [prefix + connector + self.label]
        next_prefix = prefix + ("    " if is_last else "│   ")
        for index, child in enumerate(self.children):
            child_is_last = index == len(self.children) - 1
            lines.extend(child._to_ascii_lines(next_prefix, child_is_last))
        return lines


@dataclass
class ParseTraceStep:
    """Paso individual de la traza del parser predictivo LL(1)."""

    paso: int
    pila: str
    lookahead: str
    accion: str
    celda: str = ""


@dataclass
class ParseResult:
    """Resultado unificado de cualquier método de análisis sintáctico."""

    metodo: str
    valido: bool
    arbol: Optional[ParseNode]
    error: Optional[SyntaxErrorInfo] = None
    trace: List[ParseTraceStep] = field(default_factory=list)

    @property
    def mensaje(self) -> str:
        if self.valido:
            return f"Cadena válida según el método {self.metodo}."
        return str(self.error) if self.error else f"La cadena es inválida según el método {self.metodo}."
