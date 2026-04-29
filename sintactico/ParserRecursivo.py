"""
parser_recursive.py — analizador sintáctico descendente recursivo
Compiladores — Entrega 2 | Lenguaje fuente → TypeScript
"""

from typing import List

from grammar import (
    EOF_SYMBOL,
    GRAMMAR,
    EPSILON,
    display_symbol,
    is_nonterminal,
    sanitize_nonterminal,
    token_to_terminal,
)
from parse_tree import ParseNode, ParseResult, ParserAbort, raise_syntax_error
from parser_state import LL1_TABLE
from tokens import Token


class RecursiveDescentParser:
    """Parser descendente recursivo guiado por la gramática LL(1)."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.table = LL1_TABLE
        self._partial_root = None

    def parse(self) -> ParseResult:
        """Ejecuta el análisis recursivo y devuelve ParseResult."""
        raiz = None
        self._partial_root = None
        try:
            raiz = self.parse_programa()
            self._partial_root = raiz
            if token_to_terminal(self._current_token()) != EOF_SYMBOL:
                self._raise_expected({EOF_SYMBOL}, "Se esperaba el fin del programa")
            return ParseResult(metodo="recursivo", valido=True, arbol=raiz)
        except ParserAbort as exc:
            return ParseResult(
                metodo="recursivo",
                valido=False,
                arbol=raiz or self._partial_root,
                error=exc.error,
            )

    def _current_token(self) -> Token:
        """Token en la posición actual o el último si se pasó del final."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def _lookahead(self) -> str:
        """Terminal correspondiente al token actual."""
        return token_to_terminal(self._current_token())

    def _parse_nonterminal(self, nonterminal: str) -> ParseNode:
        """Expande un no-terminal consultando la tabla LL(1)."""
        node = ParseNode(display_symbol(nonterminal))
        if nonterminal == "programa" and self._partial_root is None:
            self._partial_root = node

        lookahead = self._lookahead()
        production = self.table.get(nonterminal, {}).get(lookahead)
        if production is None:
            expected = sorted(self.table.get(nonterminal, {}).keys())
            mensaje = f"No se puede expandir {display_symbol(nonterminal)} con el token actual"
            self._raise_expected(expected, mensaje)
        for symbol in production:
            if symbol == EPSILON:
                node.add_child(ParseNode(EPSILON, is_terminal=True))
                continue

            if is_nonterminal(symbol):
                parse_method = getattr(self, f"parse_{sanitize_nonterminal(symbol)}")
                child = parse_method()
                node.add_child(child)
            else:
                token = self._match_terminal(symbol)
                node.add_child(ParseNode(symbol, token=token, is_terminal=True))

        return node

    def _match_terminal(self, expected_terminal: str) -> Token:
        """Consume el token actual si coincide con el terminal esperado."""
        current = self._current_token()
        actual_terminal = token_to_terminal(current)
        if actual_terminal != expected_terminal:
            mensaje = f"Se esperaba el terminal '{expected_terminal}'"
            self._raise_expected([expected_terminal], mensaje)
        self.pos += 1
        return current

    def _raise_expected(self, expected: List[str], mensaje: str) -> None:
        raise_syntax_error(expected, mensaje, self._current_token())


def _attach_parse_methods() -> None:
    """Genera dinámicamente un método parse_<NT> por cada no-terminal."""
    def make_method(nonterminal: str):
        def method(self):
            return self._parse_nonterminal(nonterminal)

        method.__name__ = f"parse_{sanitize_nonterminal(nonterminal)}"
        method.__doc__ = f"Reconoce la producción {display_symbol(nonterminal)}."
        return method

    for nonterminal in GRAMMAR:
        method_name = f"parse_{sanitize_nonterminal(nonterminal)}"
        if hasattr(RecursiveDescentParser, method_name):
            continue
        setattr(RecursiveDescentParser, method_name, make_method(nonterminal))


_attach_parse_methods()


if __name__ == "__main__":
    from lexer import Lexer

    codigo = """funcion factorial(n: entero): entero
  si n == 0 entonces
    retornar 1
  sino
    retornar n * factorial(n - 1)
  fin_si
fin_funcion"""
    tokens, errores = Lexer(codigo).tokenizar()
    if errores:
        for error in errores:
            print(error)
    else:
        resultado = RecursiveDescentParser(tokens).parse()
        print(resultado.mensaje)
        if resultado.arbol is not None:
            print(resultado.arbol.to_ascii())
