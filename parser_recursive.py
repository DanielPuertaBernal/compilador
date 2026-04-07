"""
parser_recursive.py — analizador sintáctico descendente recursivo
Compiladores — Entrega 2 | Lenguaje fuente → TypeScript
"""

from typing import List

from grammar import (
    EOF_SYMBOL,
    GRAMMAR,
    START_SYMBOL,
    EPSILON,
    display_symbol,
    format_production,
    is_nonterminal,
    sanitize_nonterminal,
    token_to_terminal,
)
from ll1_table import build_ll1_table, compute_first_sets, compute_follow_sets
from parse_tree import ParseNode, ParseResult, ParserAbort, SyntaxErrorInfo
from tokens import Token, TokenType

FIRST_SETS = compute_first_sets()
FOLLOW_SETS = compute_follow_sets(first_sets=FIRST_SETS)
LL1_TABLE = build_ll1_table(first_sets=FIRST_SETS, follow_sets=FOLLOW_SETS)


class RecursiveDescentParser:
    """Parser descendente recursivo guiado por la gramática LL(1)."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.first_sets = FIRST_SETS
        self.follow_sets = FOLLOW_SETS
        self.table = LL1_TABLE

    def parse(self) -> ParseResult:
        raiz = None
        try:
            raiz = self.parse_programa()
            if token_to_terminal(self._current_token()) != EOF_SYMBOL:
                self._raise_expected({EOF_SYMBOL}, "Se esperaba el fin del programa")
            return ParseResult(metodo="recursivo", valido=True, arbol=raiz)
        except ParserAbort as exc:
            return ParseResult(metodo="recursivo", valido=False, arbol=raiz, error=exc.error)

    def _current_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def _lookahead(self) -> str:
        return token_to_terminal(self._current_token())

    def _parse_nonterminal(self, nonterminal: str) -> ParseNode:
        lookahead = self._lookahead()
        production = self.table.get(nonterminal, {}).get(lookahead)
        if production is None:
            expected = sorted(self.table.get(nonterminal, {}).keys())
            mensaje = f"No se puede expandir {display_symbol(nonterminal)} con el token actual"
            self._raise_expected(expected, mensaje)

        node = ParseNode(display_symbol(nonterminal))
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
        current = self._current_token()
        actual_terminal = token_to_terminal(current)
        if actual_terminal != expected_terminal:
            mensaje = f"Se esperaba el terminal '{expected_terminal}'"
            self._raise_expected([expected_terminal], mensaje)
        self.pos += 1
        return current

    def _build_hint(self, expected: List[str], current: Token) -> str:
        expected_set = set(expected)

        if current.tipo == TokenType.EOF:
            for cierre in ["fin_si", "fin_para", "fin_mientras", "fin_funcion", "fin_clase"]:
                if cierre in expected_set:
                    return f"Parece faltar `{cierre}` antes de terminar el archivo."
            return "El programa terminó antes de cerrar una estructura de control o declaración."

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

    def _raise_expected(self, expected: List[str], mensaje: str) -> None:
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


def _attach_parse_methods() -> None:
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
