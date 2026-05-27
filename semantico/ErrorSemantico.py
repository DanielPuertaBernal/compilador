"""
ErrorSemantico.py — Estructuras de datos para errores y resultado semántico
Compiladores — Entrega 4 | Lenguaje fuente → TypeScript

Tipos de error (uno por regla semántica implementada):
  TIPO_DOBLE_DECLARACION  → REGLA SEM 1
  TIPO_NO_DECLARADO       → REGLA SEM 2
  TIPO_INCOMPATIBLE       → REGLA SEM 3
  TIPO_RETORNO_INCOMP     → REGLA SEM 4
  TIPO_LLAMADA_NO_DECL    → REGLA SEM 5
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

# ── Constantes de tipo de error ───────────────────────────────────────────────

TIPO_DOBLE_DECLARACION = "doble_declaracion"    # REGLA 1
TIPO_NO_DECLARADO      = "no_declarado"         # REGLA 2
TIPO_INCOMPATIBLE      = "tipo_incompatible"    # REGLA 3
TIPO_RETORNO_INCOMP    = "retorno_incompatible" # REGLA 4
TIPO_LLAMADA_NO_DECL   = "llamada_no_declarada" # REGLA 5
TIPO_GENERICO          = "error_semantico"


# ── Entrada individual de error ───────────────────────────────────────────────

@dataclass
class ErrorSemantico:
    """
    Error semántico detectado durante el análisis.

    Contiene posición exacta (fila/columna), el lexema involucrado,
    el tipo de regla semántica violada y una sugerencia de corrección.
    """

    mensaje:    str
    fila:       int
    columna:    int
    lexema:     str
    tipo_error: str = TIPO_GENERICO
    sugerencia: str = ""
    numero:     int = 0                     # asignado al finalizar el análisis

    def __str__(self) -> str:
        return (
            f"Fila {self.fila}, col {self.columna}: "
            f"{self.mensaje}  (lexema: '{self.lexema}')"
        )

    def FormatearReporte(self) -> str:
        """Reporte detallado al estilo de las entregas anteriores (E3)."""
        lineas = [
            f"Error semántico [{self.numero}] — línea {self.fila}, columna {self.columna}",
            f"  Tipo de regla : {self.tipo_error}",
            f"  Lexema        : '{self.lexema}'",
            f"  Descripción   : {self.mensaje}",
            f"  ¿Qué hacer?   : {self.sugerencia or '—'}",
        ]
        return "\n".join(lineas)

    # Alias de compatibilidad
    def format_report(self) -> str:
        return self.FormatearReporte()


# ── Resultado del análisis semántico ─────────────────────────────────────────

@dataclass
class ResultadoSemantico:
    """
    Resultado unificado del análisis semántico.

    valido   — True si no hubo errores semánticos
    errores  — lista de ErrorSemantico detectados (puede ser vacía)
    tabla    — referencia a la TablaSimbolos resultante
    """

    valido:  bool
    errores: List[ErrorSemantico] = field(default_factory=list)
    tabla:   object = None                  # TablaSimbolos (evita import circular)

    @property
    def mensaje(self) -> str:
        if self.valido:
            return "Análisis semántico completado: programa semánticamente válido ✓"
        n = len(self.errores)
        return f"Análisis semántico: {n} error(es) semántico(s) detectado(s)."

    def FormatearReporteErrores(self) -> str:
        """Reporte completo de todos los errores."""
        if not self.errores:
            return "Sin errores semánticos."
        bloques: List[str] = []
        for i, err in enumerate(self.errores, start=1):
            err.numero = i
            bloques.append(err.FormatearReporte())
        encabezado = f"Se detectaron {len(self.errores)} error(es) semántico(s):\n"
        return encabezado + "\n\n".join(bloques)

    # Alias de compatibilidad
    def format_error_report(self) -> str:
        return self.FormatearReporteErrores()
