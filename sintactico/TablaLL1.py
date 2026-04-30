"""
ll1_table.py — Cálculo de conjuntos FIRST, FOLLOW y tabla LL(1)
Compiladores — Entrega 2 | Lenguaje fuente → TypeScript
"""

from typing import Dict, List, Sequence, Set

from sintactico.Gramatica import (
    EPSILON,
    EOF_SYMBOL,
    GRAMMAR,
    START_SYMBOL,
    MostrarSimbolo,
    FormatearProduccion,
    ObtenerTerminales,
    EsNoTerminal,
)

ConjuntosFirst = Dict[str, Set[str]]
ConjuntosFollow = Dict[str, Set[str]]
TablaLL1 = Dict[str, Dict[str, List[str]]]


def _PrimerosDeSecuencia(secuencia: Sequence[str], conjuntos_first: ConjuntosFirst) -> Set[str]:
    """Calcula FIRST de una secuencia de símbolos."""
    if not secuencia or secuencia == [EPSILON]:
        return {EPSILON}

    resultado: Set[str] = set()
    prefijo_nullable = True

    for simbolo in secuencia:
        if simbolo == EPSILON:
            resultado.add(EPSILON)
            break
        if EsNoTerminal(simbolo):
            first_simbolo = set(conjuntos_first[simbolo])
            resultado.update(first_simbolo - {EPSILON})
            if EPSILON not in first_simbolo:
                prefijo_nullable = False
                break
        else:
            resultado.add(simbolo)
            prefijo_nullable = False
            break

    if prefijo_nullable:
        resultado.add(EPSILON)

    return resultado


def CalcularConjuntosFirst(gramatica: Dict[str, List[List[str]]] = GRAMMAR) -> ConjuntosFirst:
    """Calcula los conjuntos FIRST de todos los no-terminales."""
    conjuntos: ConjuntosFirst = {nt: set() for nt in gramatica}
    cambio = True

    while cambio:
        cambio = False
        for izq, producciones in gramatica.items():
            for produccion in producciones:
                antes = len(conjuntos[izq])
                conjuntos[izq].update(_PrimerosDeSecuencia(produccion, conjuntos))
                if len(conjuntos[izq]) != antes:
                    cambio = True

    return conjuntos


def CalcularConjuntosFollow(
    gramatica: Dict[str, List[List[str]]] = GRAMMAR,
    simbolo_inicio: str = START_SYMBOL,
    conjuntos_first: ConjuntosFirst = None,
) -> ConjuntosFollow:
    """Calcula los conjuntos FOLLOW de todos los no-terminales."""
    if conjuntos_first is None:
        conjuntos_first = CalcularConjuntosFirst(gramatica)

    conjuntos: ConjuntosFollow = {nt: set() for nt in gramatica}
    conjuntos[simbolo_inicio].add(EOF_SYMBOL)

    cambio = True
    while cambio:
        cambio = False
        for izq, producciones in gramatica.items():
            for produccion in producciones:
                for indice, simbolo in enumerate(produccion):
                    if not EsNoTerminal(simbolo):
                        continue
                    sufijo = produccion[indice + 1:]
                    first_sufijo = _PrimerosDeSecuencia(sufijo, conjuntos_first)
                    antes = len(conjuntos[simbolo])
                    conjuntos[simbolo].update(first_sufijo - {EPSILON})
                    if not sufijo or EPSILON in first_sufijo:
                        conjuntos[simbolo].update(conjuntos[izq])
                    if len(conjuntos[simbolo]) != antes:
                        cambio = True

    return conjuntos


def ConstruirTablaLL1(
    gramatica: Dict[str, List[List[str]]] = GRAMMAR,
    conjuntos_first: ConjuntosFirst = None,
    conjuntos_follow: ConjuntosFollow = None,
) -> TablaLL1:
    """Construye la tabla de análisis LL(1) a partir de FIRST/FOLLOW."""
    if conjuntos_first is None:
        conjuntos_first = CalcularConjuntosFirst(gramatica)
    if conjuntos_follow is None:
        conjuntos_follow = CalcularConjuntosFollow(gramatica, START_SYMBOL, conjuntos_first)

    tabla: TablaLL1 = {nt: {} for nt in gramatica}

    for izq, producciones in gramatica.items():
        for produccion in producciones:
            first_produccion = _PrimerosDeSecuencia(produccion, conjuntos_first)

            for terminal in first_produccion - {EPSILON}:
                existente = tabla[izq].get(terminal)
                if existente is not None and existente != produccion:
                    raise ValueError(
                        f"Conflicto LL(1) en M[{izq}, {terminal}] entre {existente} y {produccion}"
                    )
                tabla[izq][terminal] = produccion

            if EPSILON in first_produccion:
                for terminal in conjuntos_follow[izq]:
                    existente = tabla[izq].get(terminal)
                    if existente is not None and existente != produccion:
                        raise ValueError(
                            f"Conflicto LL(1) en M[{izq}, {terminal}] entre {existente} y {produccion}"
                        )
                    tabla[izq][terminal] = produccion

    return tabla


def RenderizarFirstFollow(
    conjuntos_first: ConjuntosFirst,
    conjuntos_follow: ConjuntosFollow,
) -> str:
    """Genera texto plano con los conjuntos FIRST y FOLLOW."""
    lineas = ["CONJUNTOS FIRST Y FOLLOW", "=" * 72, ""]
    for nt in GRAMMAR:
        first_txt = ", ".join(sorted(conjuntos_first[nt]))
        follow_txt = ", ".join(sorted(conjuntos_follow[nt]))
        lineas.append(f"{MostrarSimbolo(nt)}")
        lineas.append(f"  FIRST  = {{ {first_txt} }}")
        lineas.append(f"  FOLLOW = {{ {follow_txt} }}")
        lineas.append("")
    return "\n".join(lineas).rstrip()


def RenderizarTablaLL1(tabla: TablaLL1) -> str:
    """Genera texto plano con la tabla LL(1) formateada."""
    terminales = ObtenerTerminales()
    columnas = ["No terminal"] + terminales

    anchos = {col: max(len(col), 12) for col in columnas}
    filas_renderizadas = []

    for nt in GRAMMAR:
        fila = {"No terminal": MostrarSimbolo(nt)}
        anchos["No terminal"] = max(anchos["No terminal"], len(fila["No terminal"]))
        for terminal in terminales:
            produccion = tabla.get(nt, {}).get(terminal)
            celda = FormatearProduccion(nt, produccion) if produccion is not None else ""
            fila[terminal] = celda
            anchos[terminal] = max(anchos[terminal], len(celda), len(terminal))
        filas_renderizadas.append(fila)

    encabezado = " | ".join(col.ljust(anchos[col]) for col in columnas)
    separador = "-+-".join("-" * anchos[col] for col in columnas)
    lineas = [encabezado, separador]

    for fila in filas_renderizadas:
        lineas.append(" | ".join(fila[col].ljust(anchos[col]) for col in columnas))

    return "\n".join(lineas)


# ── Alias de compatibilidad hacia atrás ──────────────────────────────────────
first_of_sequence = _PrimerosDeSecuencia
compute_first_sets = CalcularConjuntosFirst
compute_follow_sets = CalcularConjuntosFollow
build_ll1_table = ConstruirTablaLL1
render_first_follow_text = RenderizarFirstFollow
render_ll1_table = RenderizarTablaLL1
FirstSets = ConjuntosFirst
FollowSets = ConjuntosFollow
LL1Table = TablaLL1


if __name__ == "__main__":
    fs = CalcularConjuntosFirst()
    fol = CalcularConjuntosFollow(conjuntos_first=fs)
    tabla = ConstruirTablaLL1(conjuntos_first=fs, conjuntos_follow=fol)
    print(RenderizarFirstFollow(fs, fol))
    print()
    print(RenderizarTablaLL1(tabla))
