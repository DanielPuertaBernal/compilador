"""
parse_tree.py — Estructuras compartidas para el análisis sintáctico
Compiladores — Entrega 2 / 3 | Lenguaje fuente → TypeScript
"""

from dataclasses import dataclass, field
from typing import List, Optional

from lexico.Tokens import Token, TokenType


@dataclass
class ErrorSintactico:
    """Error sintáctico con posición precisa y contexto completo (Entrega 3)."""

    mensaje: str
    fila: int
    columna: int
    esperado: List[str] = field(default_factory=list)
    recibido_lexema: str = ""
    recibido_tipo: str = ""
    sugerencia: str = ""
    numero: int = 0

    @property
    def recibido(self) -> str:
        """Compatibilidad con código que usa .recibido."""
        return self.recibido_lexema

    def __str__(self) -> str:
        extras = []
        if self.esperado:
            extras.append("esperado: " + ", ".join(self.esperado))
        if self.recibido_lexema:
            extras.append(f"recibido: {self.recibido_lexema}")
        if self.sugerencia:
            extras.append(f"sugerencia: {self.sugerencia}")
        sufijo = f" ({'; '.join(extras)})" if extras else ""
        return f"Fila {self.fila}, col {self.columna}: {self.mensaje}{sufijo}"

    def FormatearReporte(self) -> str:
        """Formato requerido por Entrega 3, similar a gcc/clang."""
        esperado_txt = ", ".join(self.esperado) if self.esperado else "—"
        lineas = [
            f"Error sintáctico [{self.numero}] — línea {self.fila}, columna {self.columna}",
            f"  Encontrado    : lexema='{self.recibido_lexema}'  tipo={self.recibido_tipo}",
            f"  Esperado      : {esperado_txt}",
            f"  ¿Quiso decir? : {self.sugerencia or '—'}",
        ]
        return "\n".join(lineas)

    # Alias de compatibilidad
    def format_report(self) -> str:
        return self.FormatearReporte()


class AbortarAnalisis(Exception):
    """Excepción interna para cortar el análisis al primer error (modo sin recuperación)."""

    def __init__(self, error: "ErrorSintactico"):
        self.error = error
        super().__init__(str(error))


def ConstruirSugerencia(
    esperado: List[str],
    actual: Token,
    fallback_eof: str = "El programa terminó antes de cerrar una estructura de control o declaración.",
    nonterminal: str = "",
) -> str:
    """Genera sugerencia usando la IA si está disponible, con fallback basado en reglas."""
    try:
        from ia.SugerenciasIA import MODELO_IA
        encontrado = actual.lexema if actual.lexema else actual.tipo.name
        sugerencia = MODELO_IA.Sugerir(nonterminal, encontrado, list(esperado))
        if sugerencia:
            return sugerencia
    except Exception:
        pass

    conjunto_esperado = set(esperado)
    if actual.tipo == TokenType.EOF:
        for cierre in ["fin_si", "fin_para", "fin_mientras", "fin_funcion", "fin_clase"]:
            if cierre in conjunto_esperado:
                return f"Parece faltar `{cierre}` antes de terminar el archivo."
        return fallback_eof
    if actual.lexema == "*" and any(
        item in conjunto_esperado
        for item in ["NUMERO_ENTERO", "NUMERO_REAL", "IDENTIFICADOR", "(", "nuevo"]
    ):
        return "Para la potencia usa `^`; la secuencia `**` no pertenece al lenguaje fuente."
    if ":" in conjunto_esperado:
        return "Después del identificador debe aparecer `:` y luego el tipo declarado."
    if "IDENTIFICADOR" in conjunto_esperado:
        return "Se esperaba un nombre válido de variable, función, parámetro o clase."
    if "entonces" in conjunto_esperado:
        return "Después de la condición del `si` debe ir la palabra reservada `entonces`."
    if "hacer" in conjunto_esperado:
        return "Después del encabezado de `para` o `mientras` debe aparecer `hacer`."
    if ")" in conjunto_esperado:
        return "Revisa si falta cerrar un paréntesis `)`."
    if "=" in conjunto_esperado:
        return "Si buscas asignar un valor, usa `=` seguido de una expresión válida."
    return "Revisa la sintaxis en esta línea."


def ConstruirError(
    esperado: List[str],
    mensaje: str,
    actual: Token,
    fallback_eof: str = "El programa terminó antes de cerrar una estructura de control o declaración.",
    nonterminal: str = "",
) -> "ErrorSintactico":
    """Construye ErrorSintactico sin lanzar excepción."""
    lexema = actual.lexema if actual.lexema else actual.tipo.name
    tipo_tok = actual.tipo.name
    return ErrorSintactico(
        mensaje=mensaje,
        fila=actual.fila,
        columna=actual.columna,
        esperado=list(esperado),
        recibido_lexema=lexema,
        recibido_tipo=tipo_tok,
        sugerencia=ConstruirSugerencia(esperado, actual, fallback_eof, nonterminal),
    )


def LanzarErrorSintactico(
    esperado: List[str],
    mensaje: str,
    actual: Token,
    fallback_eof: str = "El programa terminó antes de cerrar una estructura de control o declaración.",
    nonterminal: str = "",
) -> None:
    """Construye ErrorSintactico y lanza AbortarAnalisis (modo sin recuperación)."""
    raise AbortarAnalisis(ConstruirError(esperado, mensaje, actual, fallback_eof, nonterminal))


def NumerarErrores(errores: List[ErrorSintactico]) -> None:
    """Asigna número secuencial a cada error en la lista."""
    for i, e in enumerate(errores, start=1):
        e.numero = i


@dataclass
class NodoArbol:
    """Nodo genérico del árbol de análisis sintáctico."""

    simbolo: str
    hijos: List["NodoArbol"] = field(default_factory=list)
    token: Optional[Token] = None
    es_terminal: bool = False

    def AgregarHijo(self, hijo: "NodoArbol") -> None:
        self.hijos.append(hijo)

    @property
    def etiqueta(self) -> str:
        if self.token is None:
            return self.simbolo
        lexema = self.token.lexema if self.token.lexema else self.token.tipo.name
        return f"{self.simbolo} [{lexema}]"

    def ComoTextoAscii(self) -> str:
        lineas = [self.etiqueta]
        for indice, hijo in enumerate(self.hijos):
            es_ultimo = indice == len(self.hijos) - 1
            lineas.extend(hijo._LineasAscii("", es_ultimo))
        return "\n".join(lineas)

    def _LineasAscii(self, prefijo: str, es_ultimo: bool) -> List[str]:
        conector = "└── " if es_ultimo else "├── "
        lineas = [prefijo + conector + self.etiqueta]
        prefijo_sig = prefijo + ("    " if es_ultimo else "│   ")
        for indice, hijo in enumerate(self.hijos):
            hijo_es_ultimo = indice == len(self.hijos) - 1
            lineas.extend(hijo._LineasAscii(prefijo_sig, hijo_es_ultimo))
        return lineas

    # ── Alias de compatibilidad ───────────────────────────────────────
    @property
    def symbol(self) -> str:
        return self.simbolo

    @property
    def children(self) -> List["NodoArbol"]:
        return self.hijos

    @property
    def is_terminal(self) -> bool:
        return self.es_terminal

    @property
    def label(self) -> str:
        return self.etiqueta

    def add_child(self, hijo: "NodoArbol") -> None:
        self.AgregarHijo(hijo)

    def to_ascii(self) -> str:
        return self.ComoTextoAscii()


@dataclass
class PasoTraza:
    """Paso individual de la traza del parser predictivo LL(1)."""

    paso: int
    pila: str
    lookahead: str
    accion: str
    celda: str = ""


@dataclass
class ResultadoAnalisis:
    """Resultado unificado de cualquier método de análisis sintáctico."""

    metodo: str
    valido: bool
    arbol: Optional[NodoArbol]
    errores: List[ErrorSintactico] = field(default_factory=list)
    traza: List[PasoTraza] = field(default_factory=list)

    # ── Alias de compatibilidad Entrega 2 ────────────────────────────
    @property
    def errors(self) -> List[ErrorSintactico]:
        return self.errores

    @property
    def trace(self) -> List[PasoTraza]:
        return self.traza

    @property
    def error(self) -> Optional[ErrorSintactico]:
        return self.errores[0] if self.errores else None

    @property
    def mensaje(self) -> str:
        if self.valido:
            return f"Cadena válida según el método {self.metodo}."
        n = len(self.errores)
        if n:
            return f"{n} error(es) sintáctico(s) detectado(s) — método {self.metodo}."
        return f"La cadena es inválida según el método {self.metodo}."

    def FormatearReporteErrores(self) -> str:
        """Reporte completo de todos los errores en el formato de Entrega 3."""
        if not self.errores:
            return "Sin errores sintácticos."
        bloques = []
        for i, err in enumerate(self.errores, start=1):
            err.numero = i
            bloques.append(err.FormatearReporte())
        encabezado = f"Se detectaron {len(self.errores)} error(es) sintáctico(s):\n"
        return encabezado + "\n\n".join(bloques)

    def format_error_report(self) -> str:
        """Alias de compatibilidad."""
        return self.FormatearReporteErrores()


# ── Alias de compatibilidad total hacia atrás ────────────────────────────────
ParseNode = NodoArbol
ParseResult = ResultadoAnalisis
ParseTraceStep = PasoTraza
SyntaxErrorInfo = ErrorSintactico
ParserAbort = AbortarAnalisis
build_hint = ConstruirSugerencia
build_error = ConstruirError
raise_syntax_error = LanzarErrorSintactico
