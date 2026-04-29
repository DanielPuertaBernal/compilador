"""
programas.py — Programas de ejemplo predefinidos para las interfaces gráficas
Compiladores — Entrega 1 / 2 / 3 | Lenguaje fuente → TypeScript

Formato de cada entrada: (nombre, codigo_fuente, es_valido)
"""

PROGRAMAS: list[tuple[str, str, bool]] = [
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
        True,
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
        True,
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
        True,
    ),
    (
        "Mientras + Logicos",
        """var contador: entero = 0
var activo: booleano = verdadero
mientras contador < 100 y activo hacer
  si contador % 2 == 0 entonces
    contador = contador + 1
  sino
    activo = falso
  fin_si
fin_mientras""",
        True,
    ),
    (
        "Retornar vacio",
        """funcion saludar()
  retornar
fin_funcion""",
        True,
    ),
]
