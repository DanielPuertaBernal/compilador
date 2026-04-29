"""
grammar.py — Gramática LL(1) del lenguaje fuente
Compiladores — Entrega 2 | Lenguaje fuente → TypeScript
"""

from typing import Dict, List, Sequence, Set

from lexico.Tokens import Token, TokenType

EPSILON = "ε"
EOF_SYMBOL = "$"
START_SYMBOL = "programa"

# Gramática factorizada para tabla LL(1) sin conflictos.
GRAMMAR: Dict[str, List[List[str]]] = {
    "programa": [["declaracion", "programa"], [EPSILON]],
    "declaracion": [["def_clase"], ["def_funcion"], ["sentencia_no_retorno"]],
    "def_clase": [["clase", "IDENTIFICADOR", "herencia_opt", "lista_miembros", "fin_clase"]],
    "herencia_opt": [["extiende", "IDENTIFICADOR"], [EPSILON]],
    "lista_miembros": [["miembro", "lista_miembros"], [EPSILON]],
    "miembro": [["modificador", "miembro_base"]],
    "miembro_base": [["def_funcion"], ["decl_atributo"]],
    "modificador": [["publico"], ["privado"], [EPSILON]],
    "decl_atributo": [["IDENTIFICADOR", ":", "tipo", "inicializacion_opt"]],
    "def_funcion": [["funcion", "IDENTIFICADOR", "(", "parametros", ")", "tipo_retorno_opt", "bloque", "fin_funcion"]],
    "tipo_retorno_opt": [[":", "tipo"], [EPSILON]],
    "parametros": [["param_lista"], [EPSILON]],
    "param_lista": [["param", "param_lista_cont"]],
    "param_lista_cont": [[",", "param", "param_lista_cont"], [EPSILON]],
    "param": [["IDENTIFICADOR", ":", "tipo"]],
    "bloque": [["sentencia_no_retorno", "sentencia_no_retorno_seq", "retorno_final_opt"], ["sent_retornar"]],
    "sentencia_no_retorno_seq": [["sentencia_no_retorno", "sentencia_no_retorno_seq"], [EPSILON]],
    "retorno_final_opt": [["sent_retornar"], [EPSILON]],
    "sentencia": [["sentencia_no_retorno"], ["sent_retornar"]],
    "sentencia_no_retorno": [["decl_variable"], ["sent_si"], ["sent_para"], ["sent_mientras"], ["sent_identificador"]],
    "decl_variable": [["var", "IDENTIFICADOR", ":", "tipo", "inicializacion_opt"]],
    "inicializacion_opt": [["=", "expresion"], [EPSILON]],
    "sent_si": [["si", "expresion", "entonces", "bloque", "rama_sino", "fin_si"]],
    "rama_sino": [["sino", "bloque"], [EPSILON]],
    "sent_para": [["para", "IDENTIFICADOR", "desde", "expresion", "hasta", "expresion", "paso_opt", "hacer", "bloque", "fin_para"]],
    "paso_opt": [["paso", "expresion"], [EPSILON]],
    "sent_mientras": [["mientras", "expresion", "hacer", "bloque", "fin_mientras"]],
    "sent_retornar": [["retornar", "expresion_opt"]],
    "expresion_opt": [["expresion"], [EPSILON]],
    "sent_identificador": [["IDENTIFICADOR", "sent_identificador_cont"], ["este", ".", "IDENTIFICADOR", "sent_post_punto"]],
    "sent_identificador_cont": [["=", "expresion"], ["(", "argumentos", ")"], [".", "IDENTIFICADOR", "sent_post_punto"]],
    "sent_post_punto": [["=", "expresion"], ["(", "argumentos", ")"], [".", "IDENTIFICADOR", "sent_post_punto"]],
    "argumentos": [["arg_lista"], [EPSILON]],
    "arg_lista": [["expresion", "arg_lista_cont"]],
    "arg_lista_cont": [[",", "expresion", "arg_lista_cont"], [EPSILON]],
    "expresion": [["disyuncion_logica"]],
    "disyuncion_logica": [["conjuncion_logica", "continuacion_disyuncion"]],
    "continuacion_disyuncion": [["o", "conjuncion_logica", "continuacion_disyuncion"], [EPSILON]],
    "conjuncion_logica": [["comparacion", "continuacion_conjuncion"]],
    "continuacion_conjuncion": [["y", "comparacion", "continuacion_conjuncion"], [EPSILON]],
    "comparacion": [["suma_o_resta", "continuacion_comparacion"]],
    "continuacion_comparacion": [["operador_comparacion", "suma_o_resta"], [EPSILON]],
    "operador_comparacion": [["=="], ["!="], ["<"], [">"], ["<="], [">="]],
    "suma_o_resta": [["multiplicacion_div_mod", "continuacion_suma_resta"]],
    "continuacion_suma_resta": [["+", "multiplicacion_div_mod", "continuacion_suma_resta"], ["-", "multiplicacion_div_mod", "continuacion_suma_resta"], [EPSILON]],
    "multiplicacion_div_mod": [["potencia", "continuacion_mul_div_mod"]],
    "continuacion_mul_div_mod": [["*", "potencia", "continuacion_mul_div_mod"], ["/", "potencia", "continuacion_mul_div_mod"], ["%", "potencia", "continuacion_mul_div_mod"], [EPSILON]],
    "potencia": [["operacion_unaria", "continuacion_potencia"]],
    "continuacion_potencia": [["^", "operacion_unaria", "continuacion_potencia"], [EPSILON]],
    "operacion_unaria": [["no", "operacion_unaria"], ["-", "operacion_unaria"], ["valor_atomico"]],
    "valor_atomico": [
        ["NUMERO_ENTERO"],
        ["NUMERO_REAL"],
        ["CADENA_LITERAL"],
        ["verdadero"],
        ["falso"],
        ["nulo"],
        ["nuevo", "IDENTIFICADOR", "(", "argumentos", ")"],
        ["este", ".", "IDENTIFICADOR", "sufijo_valor_atomico"],
        ["IDENTIFICADOR", "sufijo_valor_atomico"],
        ["(", "expresion", ")"],
    ],
    "sufijo_valor_atomico": [["(", "argumentos", ")", "acceso_encadenado_opt"], [".", "IDENTIFICADOR", "sufijo_valor_atomico"], [EPSILON]],
    "acceso_encadenado_opt": [[".", "IDENTIFICADOR", "sufijo_valor_atomico"], [EPSILON]],
    "tipo": [["entero"], ["real"], ["cadena"], ["booleano"], ["IDENTIFICADOR"]],
}

NO_TERMINALES: Set[str] = set(GRAMMAR.keys())


def EsNoTerminal(simbolo: str) -> bool:
    """Verdadero si el símbolo es un no-terminal de la gramática."""
    return simbolo in NO_TERMINALES


def MostrarSimbolo(simbolo: str) -> str:
    """Envuelve no-terminales en <> para mostrar."""
    if EsNoTerminal(simbolo):
        return f"<{simbolo}>"
    return simbolo


def SanitizarNoTerminal(simbolo: str) -> str:
    """Reemplaza guiones por _ para nombre de método Python válido."""
    return simbolo.replace("-", "_")


def TokenATerminal(token: Token) -> str:
    """Convierte un Token del lexer al terminal que usa la gramática."""
    if token.tipo == TokenType.EOF:
        return EOF_SYMBOL
    if token.tipo == TokenType.ERROR:
        return "ERROR"
    if token.tipo in {
        TokenType.IDENTIFICADOR,
        TokenType.NUMERO_ENTERO,
        TokenType.NUMERO_REAL,
        TokenType.CADENA_LITERAL,
    }:
        return token.tipo.name
    return str(token.tipo.value)


def ObtenerTerminales(gramatica: Dict[str, List[List[str]]] = GRAMMAR) -> List[str]:
    """Devuelve la lista ordenada de terminales presentes en la gramática."""
    vistos: List[str] = []
    for producciones in gramatica.values():
        for produccion in producciones:
            for simbolo in produccion:
                if simbolo in (EPSILON, EOF_SYMBOL):
                    continue
                if EsNoTerminal(simbolo):
                    continue
                if simbolo not in vistos:
                    vistos.append(simbolo)
    if EOF_SYMBOL not in vistos:
        vistos.append(EOF_SYMBOL)
    return vistos


def FormatearProduccion(izquierda: str, derecha: Sequence[str]) -> str:
    """Formatea una producción como cadena legible: <NT> → α β."""
    return f"<{izquierda}> → {' '.join(derecha)}"


# ── Alias de compatibilidad hacia atrás (usado por ll1_table.py y parsers) ──
is_nonterminal = EsNoTerminal
display_symbol = MostrarSimbolo
sanitize_nonterminal = SanitizarNoTerminal
token_to_terminal = TokenATerminal
get_terminals = ObtenerTerminales
format_production = FormatearProduccion
NON_TERMINALS = NO_TERMINALES
