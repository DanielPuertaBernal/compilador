"""
grammar.py — gramática LL(1) del lenguaje fuente
Compiladores — Entrega 2 | Lenguaje fuente → TypeScript
"""

from typing import Dict, List, Sequence, Set

from tokens import Token, TokenType

EPSILON = "ε"
EOF_SYMBOL = "$"
START_SYMBOL = "programa"

# Gramática factorizada para permitir tabla LL(1) sin conflictos.
# Nota: se introdujo `miembro_base` para resolver la ambigüedad real en
# `miembro` cuando el lookahead es `publico` o `privado`.
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

NON_TERMINALS: Set[str] = set(GRAMMAR.keys())

_SPECIAL_TOKEN_MAP = {
    "IDENTIFICADOR": TokenType.IDENTIFICADOR,
    "NUMERO_ENTERO": TokenType.NUMERO_ENTERO,
    "NUMERO_REAL": TokenType.NUMERO_REAL,
    "CADENA_LITERAL": TokenType.CADENA_LITERAL,
}

TOKEN_NAME_TO_TYPE = {
    terminal: token_type
    for terminal, token_type in _SPECIAL_TOKEN_MAP.items()
}
TOKEN_NAME_TO_TYPE.update(
    {
        token_type.value: token_type
        for token_type in TokenType
        if token_type not in {
            TokenType.IDENTIFICADOR,
            TokenType.NUMERO_ENTERO,
            TokenType.NUMERO_REAL,
            TokenType.CADENA_LITERAL,
            TokenType.EOF,
            TokenType.ERROR,
        }
    }
)


def is_nonterminal(symbol: str) -> bool:
    return symbol in NON_TERMINALS


def display_symbol(symbol: str) -> str:
    if is_nonterminal(symbol):
        return f"<{symbol}>"
    return symbol


def sanitize_nonterminal(symbol: str) -> str:
    return symbol.replace("-", "_")


def token_to_terminal(token: Token) -> str:
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


def get_terminals(grammar: Dict[str, List[List[str]]] = GRAMMAR) -> List[str]:
    seen = []
    for productions in grammar.values():
        for production in productions:
            for symbol in production:
                if symbol in (EPSILON, EOF_SYMBOL):
                    continue
                if is_nonterminal(symbol):
                    continue
                if symbol not in seen:
                    seen.append(symbol)
    if EOF_SYMBOL not in seen:
        seen.append(EOF_SYMBOL)
    return seen


def format_production(left: str, right: Sequence[str]) -> str:
    return f"<{left}> → {' '.join(right)}"


PROGRAMAS_SINTACTICOS = [
    (
        "Factorial",
        """funcion factorial(n: entero): entero
  si n == 0 entonces
    retornar 1
  sino
    retornar n * factorial(n - 1)
  fin_si
fin_funcion
var resultado: entero = factorial(5)""",
    ),
    (
        "Busqueda lineal",
        """funcion buscar(valor: entero): booleano
  var encontrado: booleano = falso
  var limite: entero = 10
  para i desde 0 hasta limite paso 1 hacer
    si i == valor entonces
      encontrado = verdadero
    fin_si
  fin_para
  retornar encontrado
fin_funcion""",
    ),
    (
        "Clase Rectangulo",
        """clase Rectangulo
  privado ancho: real
  privado alto: real
  funcion constructor(a: real, h: real)
    este.ancho = a
    este.alto = h
  fin_funcion
  funcion area(): real
    retornar este.ancho * este.alto
  fin_funcion
fin_clase
var r: Rectangulo = nuevo Rectangulo(4.0, 4.0)""",
    ),
    (
        "Retornar vacio",
        """funcion saludar()
  retornar
fin_funcion""",
    ),
    (
        "Error: falta fin_si",
        """si x > 0 entonces
  var total2: entero = 1""",
    ),
    (
        "Error: var sin tipo",
        """var z = 5""",
    ),
    (
        "Error: operador &&",
        """si x > 0 && valor > 0 entonces
  retornar verdadero
fin_si""",
    ),
    (
        "Error: operador **",
        """var resultado: real = 2 ** 8""",
    ),
]
