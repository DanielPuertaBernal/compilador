"""
parse_tree.py — estructuras compartidas para análisis sintáctico
Compiladores — Entrega 2 | Lenguaje fuente → TypeScript
"""

from dataclasses import dataclass, field
from typing import List, Optional

from tokens import Token, TokenType


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


def build_hint(
    expected: List[str],
    current: Token,
    eof_fallback: str = "El programa terminó antes de cerrar una estructura de control o declaración.",
) -> str:
    """Genera una sugerencia legible a partir del token actual y los esperados."""
    expected_set = set(expected)

    if current.tipo == TokenType.EOF:
        for cierre in ["fin_si", "fin_para", "fin_mientras", "fin_funcion", "fin_clase"]:
            if cierre in expected_set:
                return f"Parece faltar `{cierre}` antes de terminar el archivo."
        return eof_fallback

    if current.lexema == "*" and any(
        item in expected_set
        for item in ["NUMERO_ENTERO", "NUMERO_REAL", "IDENTIFICADOR", "(", "nuevo"]
    ):
        return "Para la potencia usa `^`; la secuencia `**` no pertenece al lenguaje fuente."
    if ":" in expected_set:
        return "Después del identificador debe aparecer `:` y luego el tipo declarado."
    if "IDENTIFICADOR" in expected_set:
        return "Se esperaba un nombre válido de variable, función, parámetro o clase."
    if "entonces" in expected_set:
        return "Después de la condición del `si` debe ir la palabra reservada `entonces`."
    if "hacer" in expected_set:
        return "Después del encabezado de `para` o `mientras` debe aparecer `hacer`."
    if ")" in expected_set:
        return "Revisa si falta cerrar un paréntesis `)`."
    if "=" in expected_set:
        return "Si buscas asignar un valor, usa `=` seguido de una expresión válida."
    return ""


def raise_syntax_error(
    expected: List[str],
    mensaje: str,
    current: Token,
    eof_fallback: str = "El programa terminó antes de cerrar una estructura de control o declaración.",
) -> None:
    """Construye SyntaxErrorInfo y lanza ParserAbort."""
    recibido = current.lexema if current.lexema else current.tipo.name
    error = SyntaxErrorInfo(
        mensaje=mensaje,
        fila=current.fila,
        columna=current.columna,
        esperado=list(expected),
        recibido=recibido,
        sugerencia=build_hint(expected, current, eof_fallback),
    )
    raise ParserAbort(error)


@dataclass
class ParseNode:
    """Nodo genérico del árbol de análisis sintáctico."""

    symbol: str
    children: List["ParseNode"] = field(default_factory=list)
    token: Optional[Token] = None
    is_terminal: bool = False

    def add_child(self, child: "ParseNode") -> None:
        """Añade un nodo hijo al final de la lista."""
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
