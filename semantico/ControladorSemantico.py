"""
ControladorSemantico.py — API unificada para el análisis semántico completo
Compiladores — Entrega 4 | Lenguaje fuente → TypeScript

Encadena las tres fases del compilador:
  1. Léxico   → Lexer (Entrega 1)
  2. Sintáctico → Parser con recuperación (Entrega 2/3)
  3. Semántico  → AnalizadorSemantico (Entrega 4)

La fase semántica recibe el árbol aunque el parser haya reportado errores:
esto permite detectar errores semánticos en la porción válida del AST.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from lexico.Lexer import Lexer, ErrorLexico
from sintactico.ControladorParser import SolicitudAnalisis, EjecutarAnalisis
from sintactico.ArbolSintactico import ResultadoAnalisis
from semantico.AnalizadorSemantico import AnalizadorSemantico
from semantico.ErrorSemantico import ResultadoSemantico


@dataclass
class SolicitudSemantica:
    """Parámetros para ejecutar el análisis semántico completo."""

    codigo: str
    metodo: str = "recursivo"   # "recursivo" | "predictivo"


def EjecutarAnalisisSemantico(
    solicitud: SolicitudSemantica,
) -> Tuple[List[ErrorLexico], Optional[ResultadoAnalisis], Optional[ResultadoSemantico]]:
    """
    Ejecuta léxico → sintáctico → semántico sobre el código fuente.

    Retorna (errores_lexicos, resultado_sint, resultado_sem):
      • Si hay errores léxicos:  errores_lexicos non-empty, los demás None.
      • Si hay errores sintácticos: resultado_sint.valido == False
        pero resultado_sem es calculado igualmente sobre el árbol parcial.
      • Si todo es correcto: resultado_sint.valido y resultado_sem.valido True.
    """

    # ── Fase 1: análisis léxico ───────────────────────────────────────────
    tokens, errores_lex = Lexer(solicitud.codigo).tokenizar()
    if errores_lex:
        return errores_lex, None, None

    # ── Fase 2: análisis sintáctico ───────────────────────────────────────
    # Se activa recuperación de errores para obtener el árbol más completo posible
    _, resultado_sint = EjecutarAnalisis(
        SolicitudAnalisis(
            codigo=solicitud.codigo,
            metodo=solicitud.metodo,
            recuperar=True,
        )
    )

    # ── Fase 3: análisis semántico ────────────────────────────────────────
    arbol = resultado_sint.arbol if resultado_sint is not None else None
    analizador = AnalizadorSemantico()
    resultado_sem = analizador.analizar(arbol)

    return [], resultado_sint, resultado_sem


# ── Alias de compatibilidad ───────────────────────────────────────────────────
AnalysisRequestSemantic = SolicitudSemantica
run_semantic_analysis   = EjecutarAnalisisSemantico
