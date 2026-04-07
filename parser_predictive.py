"""
parser_predictive.py — analizador sintáctico predictivo descendente LL(1)
Compiladores — Entrega 2 | Lenguaje fuente → TypeScript
"""

from typing import List, Optional, Tuple

from grammar import (
    EOF_SYMBOL,
    GRAMMAR,
    START_SYMBOL,
    EPSILON,
    display_symbol,
    format_production,
    is_nonterminal,
    token_to_terminal,
)
from ll1_table import build_ll1_table, compute_first_sets, compute_follow_sets
from parse_tree import ParseNode, ParseResult, ParseTraceStep, ParserAbort, SyntaxErrorInfo
from tokens import Token, TokenType

FIRST_SETS = compute_first_sets()
FOLLOW_SETS = compute_follow_sets(first_sets=FIRST_SETS)
LL1_TABLE = build_ll1_table(first_sets=FIRST_SETS, follow_sets=FOLLOW_SETS)


class PredictiveParser:
    """Parser LL(1) clásico usando tabla y pila explícita."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.table = LL1_TABLE
        self.trace: List[ParseTraceStep] = []

    def parse(self) -> ParseResult:
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
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def _lookahead_text(self, token: Token, terminal: str) -> str:
        if terminal == EOF_SYMBOL:
            return EOF_SYMBOL
        if token.lexema:
            return f"{terminal} [{token.lexema}]"
        return terminal

    def _stack_to_text(self, stack: List[Tuple[str, Optional[ParseNode]]]) -> str:
        return "[ " + " | ".join(display_symbol(symbol) for symbol, _ in stack) + " ]"

    def _build_hint(self, expected: List[str], current: Token) -> str:
        expected_set = set(expected)

        if current.tipo == TokenType.EOF:
            for cierre in ["fin_si", "fin_para", "fin_mientras", "fin_funcion", "fin_clase"]:
                if cierre in expected_set:
                    return f"Parece faltar `{cierre}` antes de terminar el archivo."
            return "La entrada terminó antes de que la pila pudiera cerrar todas las producciones."

        if current.lexema == "*" and any(item in expected_set for item in ["NUMERO_ENTERO", "NUMERO_REAL", "IDENTIFICADOR", "(", "nuevo"]):
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

    def _raise_error(self, expected: List[str], mensaje: str) -> None:
        current = self._current_token()
        recibido = current.lexema if current.lexema else current.tipo.name
        error = SyntaxErrorInfo(
            mensaje=mensaje,
            fila=current.fila,
            columna=current.columna,
            esperado=list(expected),
            recibido=recibido,
            sugerencia=self._build_hint(expected, current),
        )
        raise ParserAbort(error)


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
