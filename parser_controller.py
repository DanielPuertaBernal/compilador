"""
parser_controller.py — lógica de análisis sintáctico desacoplada de la GUI
Compiladores — Entrega 2 | Lenguaje fuente → TypeScript

Función pura que recibe código fuente y método, retorna resultados.
"""

from dataclasses import dataclass
from typing import List, Optional

from lexer import Lexer, ErrorLexico
from parse_tree import ParseResult
from parser_predictive import PredictiveParser
from parser_recursive import RecursiveDescentParser


@dataclass
class AnalysisRequest:
    code: str
    method: str  # "recursivo" | "predictivo"


def run_analysis(request: AnalysisRequest) -> tuple:
    """
    Ejecuta el análisis léxico y sintáctico.

    Retorna (errores_lexicos, parse_result):
      - Si hay errores léxicos, parse_result es None.
      - Si no hay errores léxicos, errores_lexicos es lista vacía.
    """
    tokens, lexical_errors = Lexer(request.code).tokenizar()
    if lexical_errors:
        return lexical_errors, None

    if request.method == "recursivo":
        result = RecursiveDescentParser(tokens).parse()
    else:
        result = PredictiveParser(tokens).parse()

    return [], result
