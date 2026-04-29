"""
parser_predictive.py — analizador sintáctico predictivo descendente LL(1)
Compiladores — Entrega 2 | Lenguaje fuente → TypeScript
"""

from typing import List, Optional, Tuple

from grammar import (
    EOF_SYMBOL,
    START_SYMBOL,
    EPSILON,
    display_symbol,
    format_production,
    is_nonterminal,
    token_to_terminal,
)
from parse_tree import ParseNode, ParseResult, ParseTraceStep, ParserAbort, raise_syntax_error
from parser_state import LL1_TABLE
from tokens import Token


class PredictiveParser:
    """Parser LL(1) clásico usando tabla y pila explícita."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.table = LL1_TABLE
        self.trace: List[ParseTraceStep] = []

    def parse(self) -> ParseResult:
        """Ejecuta el análisis predictivo con pila explícita y genera traza."""
        raiz = ParseNode(display_symbol(START_SYMBOL))
        stack: List[Tuple[str, Optional[ParseNode]]] = [(EOF_SYMBOL, None), (START_SYMBOL, raiz)]
        paso = 1

        try:
            while stack:
                pila_texto = self._stack_to_text(stack)
                current = self._current_token()
                lookahead = token_to_terminal(current)
                lookahead_text = self._lookahead_text(current, lookahead)

                top, node = stack.pop()

                if top == EOF_SYMBOL:
                    if lookahead == EOF_SYMBOL:
                        self.trace.append(
                            ParseTraceStep(paso, pila_texto, lookahead_text, "Aceptar", "M[$,$]")
                        )
                        return ParseResult(
                            metodo="predictivo LL(1)",
                            valido=True,
                            arbol=raiz,
                            trace=self.trace,
                        )
                    self._raise_error([], "Se esperaba el fin del programa")

                elif not is_nonterminal(top):
                    if top != lookahead:
                        self._raise_error([top], f"Terminal inesperado al desempilar '{top}'")
                    if node is not None:
                        node.token = current
                    self.pos += 1
                    self.trace.append(
                        ParseTraceStep(
                            paso,
                            pila_texto,
                            lookahead_text,
                            f"Consumir terminal '{top}'",
                            "—",
                        )
                    )

                else:
                    production = self.table.get(top, {}).get(lookahead)
                    if production is None:
                        expected = sorted(self.table.get(top, {}).keys())
                        self._raise_error(expected, f"No hay producción válida para {display_symbol(top)}")

                    action = format_production(top, production)
                    self.trace.append(
                        ParseTraceStep(
                            paso,
                            pila_texto,
                            lookahead_text,
                            action,
                            f"M[{display_symbol(top)}, {lookahead}]",
                        )
                    )

                    if node is not None:
                        children: List[Tuple[str, ParseNode]] = []
                        for symbol in production:
                            if symbol == EPSILON:
                                node.add_child(ParseNode(EPSILON, is_terminal=True))
                                continue
                            child = ParseNode(display_symbol(symbol) if is_nonterminal(symbol) else symbol, is_terminal=not is_nonterminal(symbol))
                            node.add_child(child)
                            children.append((symbol, child))

                        for symbol, child in reversed(children):
                            stack.append((symbol, child))

                paso += 1

            self._raise_error([], "La pila terminó sin aceptar la entrada")

        except ParserAbort as exc:
            return ParseResult(
                metodo="predictivo LL(1)",
                valido=False,
                arbol=raiz,
                error=exc.error,
                trace=self.trace,
            )

    def _current_token(self) -> Token:
        """Token en la posición actual o el último si se pasó del final."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def _lookahead_text(self, token: Token, terminal: str) -> str:
        """Texto legible del lookahead para la columna de traza."""
        if terminal == EOF_SYMBOL:
            return EOF_SYMBOL
        if token.lexema:
            return f"{terminal} [{token.lexema}]"
        return terminal

    def _stack_to_text(self, stack: List[Tuple[str, Optional[ParseNode]]]) -> str:
        """Representación textual de la pila para la traza."""
        return "[ " + " | ".join(display_symbol(symbol) for symbol, _ in stack) + " ]"

    _EOF_FALLBACK = "La entrada terminó antes de que la pila pudiera cerrar todas las producciones."

    def _raise_error(self, expected: List[str], mensaje: str) -> None:
        raise_syntax_error(expected, mensaje, self._current_token(), eof_fallback=self._EOF_FALLBACK)


if __name__ == "__main__":
    from lexer import Lexer

    codigo = """funcion saludar()
  retornar
fin_funcion"""
    tokens, errores = Lexer(codigo).tokenizar()
    if errores:
        for error in errores:
            print(error)
    else:
        resultado = PredictiveParser(tokens).parse()
        print(resultado.mensaje)
        for paso in resultado.trace:
            print(paso)
