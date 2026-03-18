"""
tokens.py — Definición de tipos de tokens y estructura Token
Compiladores — Entrega 1 | Lenguaje fuente → TypeScript
"""

from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    # ── Palabras reservadas — Tipos de datos ──────────────────────────
    ENTERO      = "entero"
    REAL        = "real"
    CADENA      = "cadena"
    BOOLEANO    = "booleano"
    NULO        = "nulo"

    # ── Palabras reservadas — Clases / OOP ───────────────────────────
    CLASE       = "clase"
    NUEVO       = "nuevo"
    ESTE        = "este"
    EXTIENDE    = "extiende"
    PUBLICO     = "publico"
    PRIVADO     = "privado"

    # ── Palabras reservadas — Funciones ──────────────────────────────
    FUNCION     = "funcion"
    RETORNAR    = "retornar"
    FIN_FUNCION = "fin_funcion"
    FIN_CLASE   = "fin_clase"

    # ── Palabras reservadas — Control ────────────────────────────────
    SI          = "si"
    ENTONCES    = "entonces"
    SINO        = "sino"
    FIN_SI      = "fin_si"
    PARA        = "para"
    DESDE       = "desde"
    HASTA       = "hasta"
    PASO        = "paso"
    HACER       = "hacer"
    FIN_PARA    = "fin_para"
    MIENTRAS    = "mientras"
    FIN_MIENTRAS= "fin_mientras"

    # ── Palabras reservadas — Lógicos ─────────────────────────────────
    Y           = "y"
    O           = "o"
    NO          = "no"

    # ── Palabras reservadas — Declaración ────────────────────────────
    VAR         = "var"

    # ── Literales booleanos ───────────────────────────────────────────
    VERDADERO   = "verdadero"
    FALSO       = "falso"

    # ── Operadores aritméticos ────────────────────────────────────────
    SUMA        = "+"
    RESTA       = "-"
    MULT        = "*"
    DIV         = "/"
    MODULO      = "%"
    POTENCIA    = "^"

    # ── Operadores relacionales ───────────────────────────────────────
    IGUAL       = "=="
    DISTINTO    = "!="
    MENOR       = "<"
    MAYOR       = ">"
    MENOR_IGUAL = "<="
    MAYOR_IGUAL = ">="

    # ── Operador de asignación ────────────────────────────────────────
    ASIGNACION  = "="

    # ── Delimitadores ─────────────────────────────────────────────────
    PAREN_IZQ   = "("
    PAREN_DER   = ")"
    COMA        = ","
    DOS_PUNTOS  = ":"
    PUNTO       = "."

    # ── Tokens léxicos (producidos por expresiones regulares) ─────────
    IDENTIFICADOR   = "IDENTIFICADOR"
    NUMERO_ENTERO   = "NUMERO_ENTERO"
    NUMERO_REAL     = "NUMERO_REAL"
    CADENA_LITERAL  = "CADENA_LITERAL"

    # ── Especiales ────────────────────────────────────────────────────
    EOF             = "EOF"
    ERROR           = "ERROR"


# Mapa de palabras reservadas → TokenType
PALABRAS_RESERVADAS: dict[str, TokenType] = {
    tt.value: tt
    for tt in TokenType
    if tt.value not in {
        "+", "-", "*", "/", "%", "^",
        "==", "!=", "<", ">", "<=", ">=", "=",
        "(", ")", ",", ":", ".",
        "IDENTIFICADOR", "NUMERO_ENTERO", "NUMERO_REAL",
        "CADENA_LITERAL", "EOF", "ERROR",
    }
}


@dataclass
class Token:
    tipo:    TokenType
    lexema:  str
    fila:    int
    columna: int

    def __repr__(self) -> str:
        return (
            f"Token({self.tipo.name}, "
            f"'{self.lexema}', "
            f"fila={self.fila}, col={self.columna})"
        )
