"""
parser_controller.py — Lógica de análisis sintáctico desacoplada de la GUI
Compiladores — Entrega 2 / 3 | Lenguaje fuente → TypeScript
"""

from dataclasses import dataclass

from lexico.Lexer import Lexer, ErrorLexico
from sintactico.ArbolSintactico import ResultadoAnalisis
from sintactico.ParserPredictivo import AnalizadorPredictivo
from sintactico.ParserRecursivo import AnalizadorRecursivo
from typing import List


@dataclass
class SolicitudAnalisis:
    """Parámetros de una solicitud de análisis sintáctico."""
    codigo: str
    metodo: str        # "recursivo" | "predictivo"
    recuperar: bool = False  # Entrega 3: activar recuperación de errores


def EjecutarAnalisis(solicitud: SolicitudAnalisis) -> tuple:
    """
    Ejecuta el análisis léxico y sintáctico.

    Retorna (errores_lexicos, resultado_analisis):
      - Si hay errores léxicos, resultado_analisis es None.
      - Si no, errores_lexicos es lista vacía.
    """
    tokens, errores_lexicos = Lexer(solicitud.codigo).tokenizar()
    if errores_lexicos:
        return errores_lexicos, None

    if solicitud.metodo == "recursivo":
        resultado = AnalizadorRecursivo(tokens, recuperar=solicitud.recuperar).Analizar()
    else:
        resultado = AnalizadorPredictivo(tokens, recuperar=solicitud.recuperar).Analizar()

    return [], resultado


# ── Alias de compatibilidad hacia atrás ──────────────────────────────────────
AnalysisRequest = SolicitudAnalisis


def run_analysis(request) -> tuple:
    """Alias de compatibilidad para código existente."""
    return EjecutarAnalisis(SolicitudAnalisis(
        codigo=request.code if hasattr(request, "code") else request.codigo,
        metodo=request.method if hasattr(request, "method") else request.metodo,
        recuperar=request.recover if hasattr(request, "recover") else request.recuperar,
    ))
