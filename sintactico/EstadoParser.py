"""
parser_state.py — estado global de la gramática LL(1)
Compiladores — Entrega 2 | Lenguaje fuente → TypeScript

Calcula FIRST, FOLLOW y la tabla LL(1) una sola vez al importarse.
Todos los módulos que necesiten estos datos deben importarlos desde aquí.
"""

from ll1_table import build_ll1_table, compute_first_sets, compute_follow_sets


def _build():
    """Calcula FIRST, FOLLOW y tabla LL(1) una sola vez al importar."""
    first = compute_first_sets()
    follow = compute_follow_sets(first_sets=first)
    table = build_ll1_table(first_sets=first, follow_sets=follow)
    return first, follow, table


FIRST_SETS, FOLLOW_SETS, LL1_TABLE = _build()
