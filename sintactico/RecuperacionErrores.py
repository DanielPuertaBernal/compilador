"""
error_recovery.py — Recuperación de errores sintácticos (modo pánico)
Compiladores — Entrega 3

Tokens de sincronización:
  Cierres de bloque : fin_si, fin_para, fin_mientras, fin_funcion, fin_clase
  Inicios de stmt   : si, mientras, para, funcion, clase, var, retornar
  Fin de entrada    : $

Al detectar un error el parser descarta tokens hasta encontrar uno de estos
y reanuda el análisis desde ese punto.
"""

from typing import List

from sintactico.Gramatica import EOF_SYMBOL, TokenATerminal
from lexico.Tokens import Token

TOKENS_SINCRONIZACION = frozenset({
    "fin_si",
    "fin_para",
    "fin_mientras",
    "fin_funcion",
    "fin_clase",
    "si",
    "mientras",
    "para",
    "funcion",
    "clase",
    "var",
    "retornar",
    EOF_SYMBOL,
})

MAX_ERRORES = 25


def SaltarASincronizacion(tokens: List[Token], pos: int) -> int:
    """
    Avanza pos hasta el primer token de sincronización (inclusive).
    Nunca supera el índice del último token (EOF).
    """
    limite = len(tokens) - 1
    while pos < limite:
        if TokenATerminal(tokens[pos]) in TOKENS_SINCRONIZACION:
            return pos
        pos += 1
    return limite


def EsTokenSync(token: Token) -> bool:
    """Verdadero si el token es un punto de sincronización."""
    return TokenATerminal(token) in TOKENS_SINCRONIZACION


# ── Alias de compatibilidad hacia atrás ──────────────────────────────────────
SYNC_TOKENS = TOKENS_SINCRONIZACION
MAX_ERRORS = MAX_ERRORES
skip_to_sync = SaltarASincronizacion
is_sync = EsTokenSync
