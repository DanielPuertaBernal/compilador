"""
ll1_table.py — cálculo de FIRST, FOLLOW y tabla LL(1)
Compiladores — Entrega 2 | Lenguaje fuente → TypeScript
"""

from typing import Dict, List, Sequence, Set

from grammar import EPSILON, EOF_SYMBOL, GRAMMAR, START_SYMBOL, display_symbol, format_production, get_terminals, is_nonterminal

FirstSets = Dict[str, Set[str]]
FollowSets = Dict[str, Set[str]]
LL1Table = Dict[str, Dict[str, List[str]]]


def first_of_sequence(sequence: Sequence[str], first_sets: FirstSets) -> Set[str]:
    if not sequence or sequence == [EPSILON]:
        return {EPSILON}

    result: Set[str] = set()
    nullable_prefix = True

    for symbol in sequence:
        if symbol == EPSILON:
            result.add(EPSILON)
            break

        if is_nonterminal(symbol):
            symbol_first = set(first_sets[symbol])
            result.update(symbol_first - {EPSILON})
            if EPSILON not in symbol_first:
                nullable_prefix = False
                break
        else:
            result.add(symbol)
            nullable_prefix = False
            break

    if nullable_prefix:
        result.add(EPSILON)

    return result


def compute_first_sets(grammar: Dict[str, List[List[str]]] = GRAMMAR) -> FirstSets:
    first_sets: FirstSets = {nonterminal: set() for nonterminal in grammar}
    changed = True

    while changed:
        changed = False
        for left, productions in grammar.items():
            for production in productions:
                before = len(first_sets[left])
                first_sets[left].update(first_of_sequence(production, first_sets))
                if len(first_sets[left]) != before:
                    changed = True

    return first_sets


def compute_follow_sets(
    grammar: Dict[str, List[List[str]]] = GRAMMAR,
    start_symbol: str = START_SYMBOL,
    first_sets: FirstSets = None,
) -> FollowSets:
    if first_sets is None:
        first_sets = compute_first_sets(grammar)

    follow_sets: FollowSets = {nonterminal: set() for nonterminal in grammar}
    follow_sets[start_symbol].add(EOF_SYMBOL)

    changed = True
    while changed:
        changed = False
        for left, productions in grammar.items():
            for production in productions:
                for index, symbol in enumerate(production):
                    if not is_nonterminal(symbol):
                        continue

                    suffix = production[index + 1 :]
                    suffix_first = first_of_sequence(suffix, first_sets)
                    before = len(follow_sets[symbol])
                    follow_sets[symbol].update(suffix_first - {EPSILON})

                    if not suffix or EPSILON in suffix_first:
                        follow_sets[symbol].update(follow_sets[left])

                    if len(follow_sets[symbol]) != before:
                        changed = True

    return follow_sets


def build_ll1_table(
    grammar: Dict[str, List[List[str]]] = GRAMMAR,
    first_sets: FirstSets = None,
    follow_sets: FollowSets = None,
) -> LL1Table:
    if first_sets is None:
        first_sets = compute_first_sets(grammar)
    if follow_sets is None:
        follow_sets = compute_follow_sets(grammar, START_SYMBOL, first_sets)

    table: LL1Table = {nonterminal: {} for nonterminal in grammar}

    for left, productions in grammar.items():
        for production in productions:
            production_first = first_of_sequence(production, first_sets)

            for terminal in production_first - {EPSILON}:
                existing = table[left].get(terminal)
                if existing is not None and existing != production:
                    raise ValueError(
                        f"Conflicto LL(1) en M[{left}, {terminal}] entre {existing} y {production}"
                    )
                table[left][terminal] = production

            if EPSILON in production_first:
                for terminal in follow_sets[left]:
                    existing = table[left].get(terminal)
                    if existing is not None and existing != production:
                        raise ValueError(
                            f"Conflicto LL(1) en M[{left}, {terminal}] entre {existing} y {production}"
                        )
                    table[left][terminal] = production

    return table


def render_first_follow_text(first_sets: FirstSets, follow_sets: FollowSets) -> str:
    lines = ["CONJUNTOS FIRST Y FOLLOW", "=" * 72, ""]
    for nonterminal in GRAMMAR:
        first_text = ", ".join(sorted(first_sets[nonterminal]))
        follow_text = ", ".join(sorted(follow_sets[nonterminal]))
        lines.append(f"{display_symbol(nonterminal)}")
        lines.append(f"  FIRST  = {{ {first_text} }}")
        lines.append(f"  FOLLOW = {{ {follow_text} }}")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_ll1_table(table: LL1Table) -> str:
    terminals = get_terminals()
    columns = ["No terminal"] + terminals

    widths = {column: max(len(column), 12) for column in columns}
    rendered_rows = []

    for nonterminal in GRAMMAR:
        row = {"No terminal": display_symbol(nonterminal)}
        widths["No terminal"] = max(widths["No terminal"], len(row["No terminal"]))
        for terminal in terminals:
            production = table.get(nonterminal, {}).get(terminal)
            cell = ""
            if production is not None:
                cell = format_production(nonterminal, production)
            row[terminal] = cell
            widths[terminal] = max(widths[terminal], len(cell), len(terminal))
        rendered_rows.append(row)

    header = " | ".join(column.ljust(widths[column]) for column in columns)
    separator = "-+-".join("-" * widths[column] for column in columns)
    lines = [header, separator]

    for row in rendered_rows:
        lines.append(" | ".join(row[column].ljust(widths[column]) for column in columns))

    return "\n".join(lines)


if __name__ == "__main__":
    first_sets = compute_first_sets()
    follow_sets = compute_follow_sets(first_sets=first_sets)
    table = build_ll1_table(first_sets=first_sets, follow_sets=follow_sets)
    print(render_first_follow_text(first_sets, follow_sets))
    print()
    print(render_ll1_table(table))
