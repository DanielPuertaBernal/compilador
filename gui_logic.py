"""
gui_logic.py — Lógica de estado del analizador léxico visual
Compiladores — Entrega 1 | Lenguaje fuente → TypeScript
"""

from dataclasses import dataclass, field
from tokens import Token, TokenType
from lexer import Lexer


# ── Programas predefinidos ────────────────────────────────────────

PROGRAMAS: list[tuple[str, str]] = [
    ("Factorial", """\
funcion factorial(n: entero): entero
  si n == 0 entonces
    retornar 1
  sino
    retornar n * factorial(n - 1)
  fin_si
fin_funcion
var resultado: entero = factorial(5)"""),

    ("Busqueda lineal", """\
funcion buscar(valor: entero): booleano
  var encontrado: booleano = falso
  var limite: entero = 10
  para i desde 0 hasta limite paso 1 hacer
    si i == valor entonces
      encontrado = verdadero
    fin_si
  fin_para
  retornar encontrado
fin_funcion"""),

    ("Clase Rectangulo", """\
clase Rectangulo
  privado ancho: real
  privado alto: real
  funcion constructor(a: real, h: real)
    este.ancho = a
    este.alto = h
  fin_funcion
  funcion area(): real
    retornar este.ancho * este.alto
  fin_funcion
fin_clase
var r: Rectangulo = nuevo Rectangulo(4.0, 4.0)"""),

    ("Mientras + Logicos", """\
var contador: entero = 0
var activo: booleano = verdadero
mientras contador < 100 y activo hacer
  si contador % 2 == 0 entonces
    contador = contador + 1
  sino
    activo = falso
  fin_si
fin_mientras"""),

    # Errores léxicos según la documentación (BNF sección 8)
    ("Errores lexicos", """\
var resultado: entero = 10 @ 2
var nombre: cadena = "Hola mundo
var edad: entero = 5
/* Este comentario no cierra
var x: entero = 1"""),
]


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


def categoria_token(tok: Token) -> str:
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


# ── Segmento de código fuente ─────────────────────────────────────

@dataclass
class Segmento:
    texto:       str
    token:       Token | None
    char_inicio: int


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
        lex = Lexer(self.codigo)
        self.tokens_todos, self.errores_todos = lex.tokenizar()
        self.paso       = 0
        self.tabla_rows = []
        self.analizado  = True
        self._construir_segmentos()

    def _construir_segmentos(self) -> None:
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
                    Segmento(texto=src[pos:ci], token=None, char_inicio=pos))
            self.segmentos.append(
                Segmento(texto=tok.lexema, token=tok, char_inicio=ci))
            pos = ci + len(tok.lexema)
        if pos < len(src):
            self.segmentos.append(
                Segmento(texto=src[pos:], token=None, char_inicio=pos))

    # ── Acciones ─────────────────────────────────────────────

    def analizar_todo(self) -> None:
        self.detener_auto()
        self.preparar()
        for tok in self.tokens_todos:
            if tok.tipo != TokenType.EOF:
                self.tabla_rows.append(tok)
        self.paso = len(self.tokens_todos)

    def siguiente_paso(self) -> bool:
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
    def token_activo(self) -> Token | None:
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
