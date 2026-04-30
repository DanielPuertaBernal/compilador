"""
parser_predictive.py — Analizador sintáctico predictivo descendente LL(1)
Compiladores — Entrega 2 / 3 | Lenguaje fuente → TypeScript

Entrega 3: parámetro recuperar=True activa recuperación en modo pánico.
"""

from typing import List, Optional, Tuple

from sintactico.RecuperacionErrores import TOKENS_SINCRONIZACION, MAX_ERRORES, SaltarASincronizacion
from sintactico.Gramatica import (
    EOF_SYMBOL,
    START_SYMBOL,
    EPSILON,
    MostrarSimbolo,
    FormatearProduccion,
    EsNoTerminal,
    TokenATerminal,
)
from sintactico.ArbolSintactico import (
    NodoArbol,
    ResultadoAnalisis,
    PasoTraza,
    AbortarAnalisis,
    ErrorSintactico,
    ConstruirError,
    NumerarErrores,
)
from sintactico.EstadoParser import TABLA_LL1
from lexico.Tokens import Token


class AnalizadorPredictivo:
    """Parser LL(1) clásico con pila explícita y soporte de recuperación en modo pánico."""

    def __init__(self, tokens: List[Token], recuperar: bool = False):
        self.tokens = tokens
        self.pos = 0
        self.tabla = TABLA_LL1
        self.recuperar = recuperar
        self.traza: List[PasoTraza] = []
        self._errores: List[ErrorSintactico] = []

    # ── API pública ───────────────────────────────────────────────────────────

    def Analizar(self) -> ResultadoAnalisis:
        raiz = NodoArbol(MostrarSimbolo(START_SYMBOL))
        pila: List[Tuple[str, Optional[NodoArbol]]] = [
            (EOF_SYMBOL, None),
            (START_SYMBOL, raiz),
        ]
        self._errores = []
        self.traza = []

        try:
            self._Ejecutar(pila, raiz)
        except AbortarAnalisis as exc:
            self._errores.append(exc.error)

        NumerarErrores(self._errores)
        valido = len(self._errores) == 0
        return ResultadoAnalisis(
            metodo="predictivo LL(1)",
            valido=valido,
            arbol=raiz,
            errores=list(self._errores),
            traza=self.traza,
        )

    # Alias de compatibilidad
    def parse(self) -> ResultadoAnalisis:
        return self.Analizar()

    # ── Loop principal ────────────────────────────────────────────────────────

    def _Ejecutar(
        self,
        pila: List[Tuple[str, Optional[NodoArbol]]],
        raiz: NodoArbol,
    ) -> None:
        paso = 1

        while pila:
            if len(self._errores) >= MAX_ERRORES:
                break

            pila_texto = self._TextoPila(pila)
            actual = self._TokenActual()
            lookahead = TokenATerminal(actual)
            lookahead_texto = self._TextoLookahead(actual, lookahead)

            cima, nodo = pila[-1]

            # ── Aceptación ────────────────────────────────────────────────────
            if cima == EOF_SYMBOL:
                if lookahead == EOF_SYMBOL:
                    self.traza.append(
                        PasoTraza(paso, pila_texto, lookahead_texto, "Aceptar", "M[$,$]")
                    )
                    pila.pop()
                    break
                err = ConstruirError([], "Se esperaba el fin del programa", actual, nonterminal="programa")
                self._RegistrarError(err, pila, paso, pila_texto, lookahead_texto)
                pila.pop()
                paso += 1
                continue

            pila.pop()

            # ── Terminal en cima ──────────────────────────────────────────────
            if not EsNoTerminal(cima):
                if cima != lookahead:
                    err = ConstruirError([cima], f"Se esperaba '{cima}'", actual)
                    self._RegistrarError(err, pila, paso, pila_texto, lookahead_texto)
                    if lookahead not in TOKENS_SINCRONIZACION:
                        self.pos += 1
                else:
                    if nodo is not None:
                        nodo.token = actual
                    self.pos += 1
                    self.traza.append(
                        PasoTraza(paso, pila_texto, lookahead_texto, f"Consumir terminal '{cima}'", "—")
                    )

            # ── No-terminal en cima ───────────────────────────────────────────
            else:
                produccion = self.tabla.get(cima, {}).get(lookahead)

                if produccion is None:
                    esperado = sorted(self.tabla.get(cima, {}).keys())
                    err = ConstruirError(
                        esperado,
                        f"No hay producción válida para {MostrarSimbolo(cima)}",
                        actual,
                        nonterminal=cima,
                    )
                    self._RegistrarError(err, pila, paso, pila_texto, lookahead_texto)
                    self.pos = SaltarASincronizacion(self.tokens, self.pos)
                    nuevo_la = TokenATerminal(self._TokenActual())
                    while pila:
                        s, _ = pila[-1]
                        if s == EOF_SYMBOL:
                            break
                        if EsNoTerminal(s) and self.tabla.get(s, {}).get(nuevo_la):
                            break
                        if not EsNoTerminal(s) and s == nuevo_la:
                            break
                        pila.pop()
                else:
                    accion = FormatearProduccion(cima, produccion)
                    self.traza.append(
                        PasoTraza(paso, pila_texto, lookahead_texto, accion, f"M[{MostrarSimbolo(cima)}, {lookahead}]")
                    )

                    if nodo is not None:
                        hijos: List[Tuple[str, NodoArbol]] = []
                        for simbolo in produccion:
                            if simbolo == EPSILON:
                                nodo.AgregarHijo(NodoArbol(EPSILON, es_terminal=True))
                                continue
                            hijo = NodoArbol(
                                MostrarSimbolo(simbolo) if EsNoTerminal(simbolo) else simbolo,
                                es_terminal=not EsNoTerminal(simbolo),
                            )
                            nodo.AgregarHijo(hijo)
                            hijos.append((simbolo, hijo))

                        for simbolo, hijo in reversed(hijos):
                            pila.append((simbolo, hijo))

            paso += 1

    # ── Manejo de errores ─────────────────────────────────────────────────────

    def _RegistrarError(
        self,
        err: ErrorSintactico,
        pila,
        paso: int,
        pila_texto: str,
        lookahead_texto: str,
    ) -> None:
        self.traza.append(
            PasoTraza(paso, pila_texto, lookahead_texto, f"ERROR: {err.mensaje}", "—")
        )
        if not self.recuperar:
            raise AbortarAnalisis(err)
        if not self._errores or self._errores[-1].fila != err.fila or self._errores[-1].columna != err.columna:
            self._errores.append(err)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _TokenActual(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def _TextoLookahead(self, token: Token, terminal: str) -> str:
        if terminal == EOF_SYMBOL:
            return EOF_SYMBOL
        if token.lexema:
            return f"{terminal} [{token.lexema}]"
        return terminal

    def _TextoPila(self, pila: List[Tuple[str, Optional[NodoArbol]]]) -> str:
        return "[ " + " | ".join(MostrarSimbolo(s) for s, _ in pila) + " ]"

    # Aliases de compatibilidad con código existente
    def _current_token(self):
        return self._TokenActual()

    def _run(self, pila, raiz):
        return self._Ejecutar(pila, raiz)

    def _record_error(self, err, pila, paso, pila_texto, la_texto):
        return self._RegistrarError(err, pila, paso, pila_texto, la_texto)

    def _stack_to_text(self, pila):
        return self._TextoPila(pila)

    def _lookahead_text(self, token, terminal):
        return self._TextoLookahead(token, terminal)

    @property
    def trace(self):
        return self.traza


# Alias de compatibilidad hacia atrás
PredictiveParser = AnalizadorPredictivo


if __name__ == "__main__":
    from lexer import Lexer

    codigo = """funcion saludar()
  retornar
fin_funcion"""
    tokens, errores = Lexer(codigo).tokenizar()
    if errores:
        for e in errores:
            print(e)
    else:
        resultado = AnalizadorPredictivo(tokens, recuperar=True).Analizar()
        print(resultado.FormatearReporteErrores() if not resultado.valido else resultado.mensaje)
