"""
parser_recursive.py — Analizador sintáctico descendente recursivo
Compiladores — Entrega 2 / 3 | Lenguaje fuente → TypeScript

Entrega 3: parámetro recuperar=True activa recuperación en modo pánico.
  Al detectar un error se registra, se descartan tokens hasta el siguiente
  token de sincronización y el análisis continúa.
"""

from typing import List

from sintactico.RecuperacionErrores import TOKENS_SINCRONIZACION, MAX_ERRORES, SaltarASincronizacion
from sintactico.Gramatica import (
    EOF_SYMBOL,
    GRAMMAR,
    EPSILON,
    MostrarSimbolo,
    EsNoTerminal,
    SanitizarNoTerminal,
    TokenATerminal,
)
from sintactico.ArbolSintactico import (
    NodoArbol,
    ResultadoAnalisis,
    AbortarAnalisis,
    ErrorSintactico,
    ConstruirError,
    LanzarErrorSintactico,
    NumerarErrores,
)
from sintactico.EstadoParser import TABLA_LL1
from lexico.Tokens import Token


class AnalizadorRecursivo:
    """Parser descendente recursivo guiado por la gramática LL(1)."""

    def __init__(self, tokens: List[Token], recuperar: bool = False):
        self.tokens = tokens
        self.pos = 0
        self.tabla = TABLA_LL1
        self.recuperar = recuperar
        self._errores: List[ErrorSintactico] = []
        self._raiz_parcial = None

    # ── API pública ───────────────────────────────────────────────────────────

    def Analizar(self) -> ResultadoAnalisis:
        raiz = None
        self._raiz_parcial = None
        self._errores = []
        try:
            raiz = self.analizar_programa()
            self._raiz_parcial = raiz
            if TokenATerminal(self._TokenActual()) != EOF_SYMBOL:
                self._ManejarError(
                    {EOF_SYMBOL},
                    "Se esperaba el fin del programa",
                    "programa",
                )
        except AbortarAnalisis as exc:
            self._errores.append(exc.error)

        NumerarErrores(self._errores)
        valido = len(self._errores) == 0
        return ResultadoAnalisis(
            metodo="recursivo",
            valido=valido,
            arbol=raiz or self._raiz_parcial,
            errores=list(self._errores),
        )

    # Alias de compatibilidad
    def parse(self) -> ResultadoAnalisis:
        return self.Analizar()

    # ── Navegación ────────────────────────────────────────────────────────────

    def _TokenActual(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def _Lookahead(self) -> str:
        return TokenATerminal(self._TokenActual())

    # ── Núcleo de análisis ────────────────────────────────────────────────────

    def _AnalizarNoTerminal(self, nonterminal: str) -> NodoArbol:
        nodo = NodoArbol(MostrarSimbolo(nonterminal))
        if nonterminal == "programa" and self._raiz_parcial is None:
            self._raiz_parcial = nodo

        lookahead = self._Lookahead()
        produccion = self.tabla.get(nonterminal, {}).get(lookahead)

        if produccion is None:
            esperado = sorted(self.tabla.get(nonterminal, {}).keys())
            self._ManejarError(
                esperado,
                f"No se puede expandir {MostrarSimbolo(nonterminal)} con el token actual",
                nonterminal,
            )
            return nodo

        for simbolo in produccion:
            if len(self._errores) >= MAX_ERRORES:
                break
            if simbolo == EPSILON:
                nodo.AgregarHijo(NodoArbol(EPSILON, es_terminal=True))
                continue
            if EsNoTerminal(simbolo):
                metodo = getattr(self, f"analizar_{SanitizarNoTerminal(simbolo)}")
                hijo = metodo()
                nodo.AgregarHijo(hijo)
            else:
                tok = self._EmparejamientoTerminal(simbolo, nonterminal)
                nodo.AgregarHijo(NodoArbol(simbolo, token=tok, es_terminal=True))

        return nodo

    def _EmparejamientoTerminal(self, terminal_esperado: str, nonterminal: str = "") -> Token:
        actual = self._TokenActual()
        if TokenATerminal(actual) != terminal_esperado:
            self._ManejarError(
                [terminal_esperado],
                f"Se esperaba '{terminal_esperado}'",
                nonterminal,
            )
            return self._TokenActual()
        self.pos += 1
        return actual

    # ── Manejo de errores y recuperación ─────────────────────────────────────

    def _ManejarError(self, esperado, mensaje: str, nonterminal: str = "") -> None:
        """
        Registra el error. En modo recuperación salta al siguiente token de
        sincronización; sin recuperación lanza AbortarAnalisis.
        """
        actual = self._TokenActual()
        err = ConstruirError(list(esperado), mensaje, actual, nonterminal=nonterminal)

        if not self.recuperar:
            raise AbortarAnalisis(err)

        if not self._errores or self._errores[-1].fila != err.fila or self._errores[-1].columna != err.columna:
            self._errores.append(err)

        if len(self._errores) >= MAX_ERRORES:
            return

        self.pos = SaltarASincronizacion(self.tokens, self.pos)

    def _LanzarEsperado(self, esperado: List[str], mensaje: str, nonterminal: str = "") -> None:
        LanzarErrorSintactico(esperado, mensaje, self._TokenActual(), nonterminal=nonterminal)

    # Aliases para compatibilidad con código existente
    def _parse_nonterminal(self, nt):
        return self._AnalizarNoTerminal(nt)

    def _match_terminal(self, terminal, nt=""):
        return self._EmparejamientoTerminal(terminal, nt)

    def _handle_error(self, esperado, mensaje, nt=""):
        return self._ManejarError(esperado, mensaje, nt)

    def _current_token(self):
        return self._TokenActual()

    def _lookahead(self):
        return self._Lookahead()


def _AgregarMetodosAnalisis() -> None:
    """Genera dinámicamente un método analizar_<NT> por cada no-terminal."""
    def _crear_metodo(nonterminal: str):
        def metodo(self):
            return self._AnalizarNoTerminal(nonterminal)
        nombre = f"analizar_{SanitizarNoTerminal(nonterminal)}"
        metodo.__name__ = nombre
        metodo.__doc__ = f"Reconoce la producción {MostrarSimbolo(nonterminal)}."
        return metodo

    for nonterminal in GRAMMAR:
        nombre_metodo = f"analizar_{SanitizarNoTerminal(nonterminal)}"
        # También generar alias parse_<NT> para compatibilidad
        nombre_alias = f"parse_{SanitizarNoTerminal(nonterminal)}"
        if not hasattr(AnalizadorRecursivo, nombre_metodo):
            setattr(AnalizadorRecursivo, nombre_metodo, _crear_metodo(nonterminal))
        if not hasattr(AnalizadorRecursivo, nombre_alias):
            setattr(AnalizadorRecursivo, nombre_alias, _crear_metodo(nonterminal))


_AgregarMetodosAnalisis()

# Alias de compatibilidad hacia atrás
RecursiveDescentParser = AnalizadorRecursivo


if __name__ == "__main__":
    from lexer import Lexer

    codigo = """funcion factorial(n: entero): entero
  si n == 0
    retornar 1
  sino
    retornar n * factorial(n - 1)
  fin_si
fin_funcion"""
    tokens, errores = Lexer(codigo).tokenizar()
    if errores:
        for e in errores:
            print(e)
    else:
        resultado = AnalizadorRecursivo(tokens, recuperar=True).Analizar()
        print(resultado.FormatearReporteErrores() if not resultado.valido else resultado.mensaje)
        if resultado.arbol is not None:
            print(resultado.arbol.ComoTextoAscii())
