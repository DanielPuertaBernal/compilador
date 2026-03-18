"""
main.py — Interfaz interactiva del analizador léxico
Compiladores — Entrega 1 | Lenguaje fuente → TypeScript

Modos de uso:
  1. Ingresar código manualmente por consola
  2. Seleccionar un programa predefinido del menú
"""

from lexer import Lexer
from tokens import Token, TokenType

# ─────────────────────────────────────────────────────────────────────
# Colores ANSI para consola
# ─────────────────────────────────────────────────────────────────────

class Color:
    RESET       = "\033[0m"
    BOLD        = "\033[1m"
    # Categorías de tokens
    RESERVADA   = "\033[38;5;81m"    # azul claro  — palabras reservadas
    TIPO        = "\033[38;5;114m"   # verde claro — tipos de datos
    LOGICO      = "\033[38;5;213m"   # rosa        — operadores lógicos
    OPERADOR    = "\033[38;5;220m"   # amarillo    — operadores aritmét./relac.
    DELIMITADOR = "\033[38;5;245m"   # gris        — delimitadores
    IDENTIFICADOR = "\033[38;5;255m" # blanco      — identificadores
    NUMERO      = "\033[38;5;208m"   # naranja     — números
    CADENA_LIT  = "\033[38;5;178m"   # dorado      — cadenas de texto
    BOOLEANO    = "\033[38;5;141m"   # lila        — verdadero / falso
    ERROR       = "\033[38;5;196m"   # rojo        — errores
    TITULO      = "\033[38;5;39m"    # azul        — títulos
    SEPARADOR   = "\033[38;5;240m"   # gris oscuro — líneas


# ─────────────────────────────────────────────────────────────────────
# Clasificación de tokens por categoría visual
# ─────────────────────────────────────────────────────────────────────

TIPOS_DATOS = {
    TokenType.ENTERO, TokenType.REAL, TokenType.CADENA, TokenType.BOOLEANO, TokenType.NULO
}

PALABRAS_CONTROL = {
    TokenType.SI, TokenType.ENTONCES, TokenType.SINO, TokenType.FIN_SI,
    TokenType.PARA, TokenType.DESDE, TokenType.HASTA, TokenType.PASO,
    TokenType.HACER, TokenType.FIN_PARA, TokenType.MIENTRAS, TokenType.FIN_MIENTRAS,
    TokenType.CLASE, TokenType.NUEVO, TokenType.ESTE, TokenType.EXTIENDE,
    TokenType.PUBLICO, TokenType.PRIVADO, TokenType.FUNCION, TokenType.RETORNAR,
    TokenType.FIN_FUNCION, TokenType.FIN_CLASE, TokenType.VAR,
}

LOGICOS = {TokenType.Y, TokenType.O, TokenType.NO}

OPERADORES = {
    TokenType.SUMA, TokenType.RESTA, TokenType.MULT, TokenType.DIV,
    TokenType.MODULO, TokenType.POTENCIA, TokenType.IGUAL, TokenType.DISTINTO,
    TokenType.MENOR, TokenType.MAYOR, TokenType.MENOR_IGUAL, TokenType.MAYOR_IGUAL,
    TokenType.ASIGNACION,
}

DELIMITADORES = {
    TokenType.PAREN_IZQ, TokenType.PAREN_DER,
    TokenType.COMA, TokenType.DOS_PUNTOS, TokenType.PUNTO,
}

BOOLEANOS = {TokenType.VERDADERO, TokenType.FALSO}


def color_de_token(tok: Token) -> str:
    if tok.tipo == TokenType.ERROR:
        return Color.ERROR
    if tok.tipo in TIPOS_DATOS:
        return Color.TIPO
    if tok.tipo in PALABRAS_CONTROL:
        return Color.RESERVADA
    if tok.tipo in LOGICOS:
        return Color.LOGICO
    if tok.tipo in OPERADORES:
        return Color.OPERADOR
    if tok.tipo in DELIMITADORES:
        return Color.DELIMITADOR
    if tok.tipo == TokenType.IDENTIFICADOR:
        return Color.IDENTIFICADOR
    if tok.tipo in (TokenType.NUMERO_ENTERO, TokenType.NUMERO_REAL):
        return Color.NUMERO
    if tok.tipo == TokenType.CADENA_LITERAL:
        return Color.CADENA_LIT
    if tok.tipo in BOOLEANOS:
        return Color.BOOLEANO
    return Color.RESET


# ─────────────────────────────────────────────────────────────────────
# Programas predefinidos
# ─────────────────────────────────────────────────────────────────────

PROGRAMAS = {
    "1": (
        "Factorial recursivo",
        """\
funcion factorial(n: entero): entero
  si n == 0 entonces
    retornar 1
  sino
    retornar n * factorial(n - 1)
  fin_si
fin_funcion

var resultado: entero = factorial(5)
"""
    ),
    "2": (
        "Búsqueda lineal con para",
        """\
funcion buscar(valor: entero): booleano
  var encontrado: booleano = falso
  var limite: entero = 10

  para i desde 0 hasta limite paso 1 hacer
    si i == valor entonces
      encontrado = verdadero
    fin_si
  fin_para

  retornar encontrado
fin_funcion
"""
    ),
    "3": (
        "Clase Rectangulo — OOP completo",
        """\
clase Rectangulo
  privado ancho: real
  privado alto: real

  funcion constructor(a: real, h: real)
    este.ancho = a
    este.alto = h
  fin_funcion

  funcion area(): real
    retornar este.ancho * este.alto
  fin_funcion

  funcion esCuadrado(): booleano
    si este.ancho == este.alto entonces
      retornar verdadero
    sino
      retornar falso
    fin_si
  fin_funcion

fin_clase

var r: Rectangulo = nuevo Rectangulo(4.0, 4.0)
var resultado: booleano = r.esCuadrado()
"""
    ),
    "4": (
        "Mientras y operadores lógicos",
        """\
var contador: entero = 0
var limite: entero = 100
var activo: booleano = verdadero

mientras contador < limite y activo hacer
  si contador % 2 == 0 entonces
    contador = contador + 1
  sino
    activo = falso
  fin_si
fin_mientras
"""
    ),
    "5": (
        "Errores léxicos — carácter inválido y cadena sin cerrar",
        """\
var resultado: entero = 10 @ 2
var nombre: cadena = "Hola mundo
var edad: entero = 5
"""
    ),
}


# ─────────────────────────────────────────────────────────────────────
# Visualización
# ─────────────────────────────────────────────────────────────────────

def imprimir_separador(ancho: int = 70):
    print(f"{Color.SEPARADOR}{'─' * ancho}{Color.RESET}")


def imprimir_titulo(texto: str):
    print(f"\n{Color.TITULO}{Color.BOLD}{'═' * 70}{Color.RESET}")
    print(f"{Color.TITULO}{Color.BOLD}  {texto}{Color.RESET}")
    print(f"{Color.TITULO}{Color.BOLD}{'═' * 70}{Color.RESET}\n")


def imprimir_leyenda():
    print(f"{Color.BOLD}  Leyenda de colores:{Color.RESET}")
    categorias = [
        (Color.RESERVADA,    "Palabra reservada (control/clase/función)"),
        (Color.TIPO,         "Tipo de dato (entero, real, cadena, booleano)"),
        (Color.LOGICO,       "Operador lógico (y, o, no)"),
        (Color.OPERADOR,     "Operador aritmético / relacional"),
        (Color.DELIMITADOR,  "Delimitador ( ) , : ."),
        (Color.IDENTIFICADOR,"Identificador"),
        (Color.NUMERO,       "Número (entero o real)"),
        (Color.CADENA_LIT,   "Cadena literal"),
        (Color.BOOLEANO,     "Booleano (verdadero / falso)"),
        (Color.ERROR,        "Error léxico"),
    ]
    for color, desc in categorias:
        print(f"    {color}■{Color.RESET}  {desc}")
    print()


def visualizar_tokens(tokens: list[Token]):
    """Muestra la cadena de tokens coloreada por categoría."""
    print(f"{Color.BOLD}  Tokens reconocidos:{Color.RESET}\n  ", end="")
    col_actual = 0
    for tok in tokens:
        if tok.tipo == TokenType.EOF:
            break
        color  = color_de_token(tok)
        texto  = tok.lexema
        espacio = " "
        if col_actual + len(texto) > 65:
            print(f"\n  ", end="")
            col_actual = 0
        print(f"{color}{texto}{Color.RESET}{espacio}", end="")
        col_actual += len(texto) + 1
    print("\n")


def imprimir_tabla(tokens: list[Token]):
    """Imprime la tabla de símbolos léxicos."""
    col_w = [20, 22, 6, 8]
    header = (
        f"{'Lexema':<{col_w[0]}}"
        f"{'Categoría (TokenType)':<{col_w[1]}}"
        f"{'Fila':>{col_w[2]}}"
        f"{'Columna':>{col_w[3]}}"
    )
    imprimir_separador()
    print(f"{Color.BOLD}  {header}{Color.RESET}")
    imprimir_separador()

    for tok in tokens:
        if tok.tipo == TokenType.EOF:
            break
        color  = color_de_token(tok)
        lexema = tok.lexema if len(tok.lexema) <= 19 else tok.lexema[:16] + "..."
        print(
            f"  {color}{lexema:<{col_w[0]}}"
            f"{tok.tipo.name:<{col_w[1]}}"
            f"{tok.fila:>{col_w[2]}}"
            f"{tok.columna:>{col_w[3]}}{Color.RESET}"
        )

    imprimir_separador()
    total = sum(1 for t in tokens if t.tipo != TokenType.EOF)
    print(f"  {Color.BOLD}Total de tokens: {total}{Color.RESET}\n")


def imprimir_errores(errores):
    """Imprime los errores léxicos encontrados."""
    if not errores:
        print(f"  {Color.TIPO}✓ Sin errores léxicos.{Color.RESET}\n")
        return

    print(f"  {Color.ERROR}{Color.BOLD}Errores léxicos encontrados: {len(errores)}{Color.RESET}")
    for e in errores:
        print(f"  {Color.ERROR}✗ Fila {e.fila}, columna {e.columna}: {e.mensaje}{Color.RESET}")
    print()


# ─────────────────────────────────────────────────────────────────────
# Flujo principal
# ─────────────────────────────────────────────────────────────────────

def analizar(codigo: str, nombre: str = "Entrada"):
    imprimir_titulo(f"Análisis léxico — {nombre}")
    print(f"{Color.SEPARADOR}  Código fuente:{Color.RESET}")
    for i, linea in enumerate(codigo.splitlines(), 1):
        print(f"  {Color.SEPARADOR}{i:3}│{Color.RESET}  {linea}")
    print()

    lex = Lexer(codigo)
    tokens, errores = lex.tokenizar()

    imprimir_leyenda()
    visualizar_tokens(tokens)

    print(f"{Color.BOLD}  Tabla de símbolos léxicos:{Color.RESET}\n")
    imprimir_tabla(tokens)

    print(f"{Color.BOLD}  Reporte de errores léxicos:{Color.RESET}\n")
    imprimir_errores(errores)


def menu_predefinidos():
    imprimir_titulo("Programas predefinidos")
    for clave, (nombre, _) in PROGRAMAS.items():
        print(f"  {Color.TITULO}{clave}{Color.RESET}. {nombre}")
    print(f"  {Color.SEPARADOR}0. Volver{Color.RESET}\n")

    opcion = input("  Selecciona un programa: ").strip()
    if opcion in PROGRAMAS:
        nombre, codigo = PROGRAMAS[opcion]
        analizar(codigo, nombre)
    elif opcion != "0":
        print(f"  {Color.ERROR}Opción no válida.{Color.RESET}\n")


def menu_principal():
    imprimir_titulo("Analizador Léxico — Lenguaje Fuente → TypeScript")
    while True:
        print(f"  {Color.TITULO}1{Color.RESET}. Ingresar código manualmente")
        print(f"  {Color.TITULO}2{Color.RESET}. Seleccionar programa predefinido")
        print(f"  {Color.SEPARADOR}0. Salir{Color.RESET}\n")

        opcion = input("  Opción: ").strip()

        if opcion == "1":
            print(f"\n  {Color.BOLD}Escribe tu código fuente.")
            print(f"  {Color.SEPARADOR}Escribe 'FIN' en una línea vacía para terminar.{Color.RESET}\n")
            lineas = []
            while True:
                try:
                    linea = input()
                except EOFError:
                    break
                if linea.strip() == "FIN":
                    break
                lineas.append(linea)
            codigo = "\n".join(lineas)
            if codigo.strip():
                analizar(codigo, "Entrada manual")
            else:
                print(f"  {Color.ERROR}No ingresaste código.{Color.RESET}\n")

        elif opcion == "2":
            menu_predefinidos()

        elif opcion == "0":
            print(f"\n  {Color.TITULO}¡Hasta luego!{Color.RESET}\n")
            break
        else:
            print(f"  {Color.ERROR}Opción no válida.{Color.RESET}\n")


if __name__ == "__main__":
    menu_principal()
