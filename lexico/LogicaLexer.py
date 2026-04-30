"""
gui_logic.py — Lógica de estado del analizador léxico visual
Compiladores — Entrega 1 | Lenguaje fuente → TypeScript
"""

from dataclasses import dataclass, field
from typing import Optional

from lexico.Tokens import Token, TokenType
from lexico.Lexer import Lexer
from gui.Programas import PROGRAMAS as _PROGRAMAS_FULL


# ── Programas predefinidos (subconjunto léxico: nombre, código) ───

PROGRAMAS: list[tuple[str, str]] = [(n, c) for n, c, _ in _PROGRAMAS_FULL]


# ── Categorías de token ───────────────────────────────────────────

_TIPOS_DATOS   = {TokenType.ENTERO, TokenType.REAL, TokenType.CADENA,
                  TokenType.BOOLEANO, TokenType.NULO}
_TIPOS_LOGICOS = {TokenType.Y, TokenType.O, TokenType.NO}
_BOOLEANOS     = {TokenType.VERDADERO, TokenType.FALSO}
_OPERADORES    = {TokenType.SUMA, TokenType.RESTA, TokenType.MULT,
                  TokenType.DIV, TokenType.MODULO, TokenType.POTENCIA,
                  TokenType.IGUAL, TokenType.DISTINTO, TokenType.MENOR,
                  TokenType.MAYOR, TokenType.MENOR_IGUAL, TokenType.MAYOR_IGUAL,
                  TokenType.ASIGNACION}
_DELIMITADORES = {TokenType.PAREN_IZQ, TokenType.PAREN_DER,
                  TokenType.COMA, TokenType.DOS_PUNTOS, TokenType.PUNTO}


def CategoriaToken(tok: Token) -> str:
    """Clasifica un TokenType en su categoría visual para la UI."""
    if tok.tipo == TokenType.ERROR:           return "error"
    if tok.tipo == TokenType.IDENTIFICADOR:   return "identificador"
    if tok.tipo in (TokenType.NUMERO_ENTERO,
                    TokenType.NUMERO_REAL):   return "numero"
    if tok.tipo == TokenType.CADENA_LITERAL:  return "cadena"
    if tok.tipo in _BOOLEANOS:                return "booleano"
    if tok.tipo in _TIPOS_LOGICOS:            return "logico"
    if tok.tipo in _TIPOS_DATOS:              return "tipo"
    if tok.tipo in _OPERADORES:               return "operador"
    if tok.tipo in _DELIMITADORES:            return "delimitador"
    return "reservada"


# Alias de compatibilidad
categoria_token = CategoriaToken


# ── Segmento de código fuente ─────────────────────────────────────

@dataclass
class SegmentoCodigo:
    texto:       str
    token:       Optional[Token]
    char_inicio: int


# Alias de compatibilidad
Segmento = SegmentoCodigo


# ── Estado principal ──────────────────────────────────────────────

@dataclass
class EstadoLexer:
    codigo:         str            = field(default_factory=lambda: PROGRAMAS[0][1])
    tokens_todos:   list           = field(default_factory=list)
    errores_todos:  list           = field(default_factory=list)
    paso:           int            = 0
    analizado:      bool           = False
    tabla_rows:     list           = field(default_factory=list)
    segmentos:      list           = field(default_factory=list)
    auto:           bool           = False
    auto_ms:        int            = 0
    auto_speed:     int            = 300

    def preparar(self) -> None:
        """Inicializa el lexer con código nuevo y resetea el estado."""
        lex = Lexer(self.codigo)
        self.tokens_todos, self.errores_todos = lex.tokenizar()
        self.paso       = 0
        self.tabla_rows = []
        self.analizado  = True
        self._construir_segmentos()

    def _construir_segmentos(self) -> None:
        """Divide el código en segmentos coloreables por posición de token."""
        self.segmentos = []
        src = self.codigo
        pos = 0
        for tok in self.tokens_todos:
            if tok.tipo == TokenType.EOF:
                break
            lineas   = src.split('\n')
            ci       = sum(len(lineas[l]) + 1 for l in range(tok.fila - 1))
            ci      += tok.columna - 1          # ← .columna correcto
            if ci > pos:
                self.segmentos.append(
                    SegmentoCodigo(texto=src[pos:ci], token=None, char_inicio=pos))
            self.segmentos.append(
                SegmentoCodigo(texto=tok.lexema, token=tok, char_inicio=ci))
            pos = ci + len(tok.lexema)
        if pos < len(src):
            self.segmentos.append(
                SegmentoCodigo(texto=src[pos:], token=None, char_inicio=pos))

    # ── Acciones ─────────────────────────────────────────────

    def analizar_todo(self) -> None:
        """Tokeniza el código completo de una vez."""
        self.detener_auto()
        self.preparar()
        for tok in self.tokens_todos:
            if tok.tipo != TokenType.EOF:
                self.tabla_rows.append(tok)
        self.paso = len(self.tokens_todos)

    def siguiente_paso(self) -> bool:
        """Avanza al siguiente token en modo paso a paso."""
        if not self.analizado:
            self.preparar()
        if self.paso < len(self.tokens_todos):
            tok = self.tokens_todos[self.paso]
            if tok.tipo != TokenType.EOF:
                self.tabla_rows.append(tok)
            self.paso += 1
        return self.paso < len(self.tokens_todos)

    def reiniciar(self) -> None:
        self.detener_auto()
        self.tokens_todos  = []
        self.errores_todos = []
        self.paso          = 0
        self.analizado     = False
        self.tabla_rows    = []
        self.segmentos     = []

    def toggle_auto(self) -> None:
        self.auto = not self.auto
        if self.auto and not self.analizado:
            self.preparar()

    def detener_auto(self) -> None:
        self.auto    = False
        self.auto_ms = 0

    def tick_auto(self, dt_ms: int) -> None:
        if not self.auto:
            return
        self.auto_ms += dt_ms
        if self.auto_ms >= self.auto_speed:
            self.auto_ms = 0
            if not self.siguiente_paso():
                self.detener_auto()

    # ── Consultas ─────────────────────────────────────────────

    @property
    def token_activo(self) -> Optional[Token]:
        if 0 < self.paso <= len(self.tokens_todos):
            tok = self.tokens_todos[self.paso - 1]
            return tok if tok.tipo != TokenType.EOF else None
        return None

    @property
    def total_tokens(self) -> int:
        return sum(1 for t in self.tokens_todos if t.tipo != TokenType.EOF)

    @property
    def progreso(self) -> float:
        if not self.tokens_todos:
            return 0.0
        return min(1.0, self.paso / len(self.tokens_todos))

    @property
    def finalizado(self) -> bool:
        return self.analizado and self.paso >= len(self.tokens_todos)
