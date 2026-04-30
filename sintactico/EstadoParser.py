"""
parser_state.py — Estado global de la gramática LL(1)
Compiladores — Entrega 2 | Lenguaje fuente → TypeScript

Calcula FIRST, FOLLOW y la tabla LL(1) una sola vez al importarse.
Todos los módulos que necesiten estos datos deben importarlos desde aquí.
"""

from sintactico.TablaLL1 import CalcularConjuntosFirst, CalcularConjuntosFollow, ConstruirTablaLL1


def _Construir():
    """Calcula FIRST, FOLLOW y tabla LL(1) una sola vez al importar."""
    first = CalcularConjuntosFirst()
    follow = CalcularConjuntosFollow(conjuntos_first=first)
    tabla = ConstruirTablaLL1(conjuntos_first=first, conjuntos_follow=follow)
    return first, follow, tabla


CONJUNTOS_FIRST, CONJUNTOS_FOLLOW, TABLA_LL1 = _Construir()

# Alias de compatibilidad hacia atrás
FIRST_SETS = CONJUNTOS_FIRST
FOLLOW_SETS = CONJUNTOS_FOLLOW
LL1_TABLE = TABLA_LL1
