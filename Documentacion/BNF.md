# Gramática Libre de Contexto — Notación BNF
**Teoría de Compiladores — Trabajo de curso | Entrega 2**

---

## 1. Descripción informal del lenguaje

El lenguaje fuente es un lenguaje imperativo orientado a objetos con palabras reservadas en
español. Compila a TypeScript. Soporta tipos estáticos, clases con atributos y métodos,
funciones independientes, estructuras de control clásicas y expresiones aritméticas,
relacionales y lógicas.

### Características generales

- **Tipado:** estático y explícito — toda variable y parámetro debe declarar su tipo.
- **Alcance:** las variables declaradas dentro de un bloque (`hacer … fin_*`) son locales a ese bloque.
- **Paradigma:** orientado a objetos; las clases pueden tener atributos públicos y privados, y métodos definidos con `funcion`.
- **Comentarios:** de línea con `//` y de bloque con `/* … */` — ignorados por el analizador léxico.
- **Sensibilidad a mayúsculas:** el lenguaje distingue entre mayúsculas y minúsculas en identificadores.

---

## 2. Conjunto de terminales

### 2.1 Palabras reservadas

```
var        funcion    retornar   clase      nuevo      este
extiende   publico    privado    si         entonces   sino
fin_si     para       desde      hasta      paso       hacer
fin_para   mientras   fin_mientras  fin_funcion  fin_clase
entero     real       cadena     booleano   nulo
verdadero  falso      y          o          no
```

### 2.2 Operadores

```
+   -   *   /   %   ^        /* aritméticos */
==  !=  <   >   <=  >=       /* relacionales */
=                            /* asignación */
```

### 2.3 Delimitadores

```
(   )   ,   :   "   .
```

### 2.4 Tokens léxicos

| Token | Expresión regular | Ejemplo |
|---|---|---|
| `IDENTIFICADOR` | `letra (letra \| digito)*` | `miVariable`, `calcularÁrea` |
| `NUMERO_ENTERO` | `digito+` | `0`, `42`, `1000` |
| `NUMERO_REAL` | `digito+ '.' digito+` | `3.14`, `0.5` |
| `CADENA_LITERAL` | `'"' (cualquier_carácter)* '"'` | `"Hola"` |

Donde:
- `letra` = `[a-z] | [A-Z] | [á-ú] | [Á-Ú] | ñ | Ñ`
- `digito` = `[0-9]`

---

## 3. Producciones BNF

> **Convenciones:**
> - `ε` representa la producción vacía (épsilon).
> - Los terminales aparecen entre `"comillas"` o como palabras reservadas en español.
> - Los no-terminales se escriben entre `< >`.
> - Toda repetición se expresa con recursividad derecha explícita — sin notación `*` ni `+`.

---

### 3.1 Programa

```bnf
<programa> ::= <declaracion> <programa>
             | ε
```

```bnf
<declaracion> ::= <def_clase>
               | <def_funcion>
               | <sentencia_no_retorno>
```

---

### 3.2 Definición de clase

```bnf
<def_clase> ::= clase IDENTIFICADOR <herencia_opt>
                  <lista_miembros>
                fin_clase

<herencia_opt> ::= extiende IDENTIFICADOR
                 | ε

<lista_miembros> ::= <miembro> <lista_miembros>
                   | ε
```

```bnf
<miembro> ::= <modificador> <miembro_base>

<miembro_base> ::= <def_funcion>
                 | <decl_atributo>

<modificador> ::= publico
               | privado
               | ε

<decl_atributo> ::= IDENTIFICADOR ":" <tipo> <inicializacion_opt>

<inicializacion_opt> ::= "=" <expresion>
                       | ε
```

---

### 3.3 Definición de función / método

```bnf
<def_funcion> ::= funcion IDENTIFICADOR "(" <parametros> ")" <tipo_retorno_opt>
                    <bloque>
                  fin_funcion

<tipo_retorno_opt> ::= ":" <tipo>
                     | ε

<parametros> ::= <param_lista>
               | ε

<param_lista>      ::= <param> <param_lista_cont>
<param_lista_cont> ::= "," <param> <param_lista_cont>
                     | ε

<param> ::= IDENTIFICADOR ":" <tipo>
```

---

### 3.4 Bloque y sentencias

```bnf
<bloque> ::= <sentencia_no_retorno> <sentencia_no_retorno_seq> <retorno_final_opt>
           | <sent_retornar>

<sentencia_no_retorno_seq> ::= <sentencia_no_retorno> <sentencia_no_retorno_seq>
                             | ε

<retorno_final_opt> ::= <sent_retornar>
                      | ε
```

```bnf
<sentencia> ::= <sentencia_no_retorno>
              | <sent_retornar>

<sentencia_no_retorno> ::= <decl_variable>
                         | <sent_si>
                         | <sent_para>
                         | <sent_mientras>
                         | <sent_identificador>
```

---

### 3.5 Declaración de variable

```bnf
<decl_variable> ::= var IDENTIFICADOR ":" <tipo> <inicializacion_opt>

<inicializacion_opt> ::= "=" <expresion>
                       | ε
```

---

### 3.6 Sentencia iniciada por identificador — asignación o llamada

```bnf
<sent_identificador> ::= IDENTIFICADOR <sent_identificador_cont>
                       | este "." IDENTIFICADOR <sent_post_punto>

<sent_identificador_cont> ::= "=" <expresion>
                            | "(" <argumentos> ")"
                            | "." IDENTIFICADOR <sent_post_punto>

<sent_post_punto> ::= "=" <expresion>
                    | "(" <argumentos> ")"
                    | "." IDENTIFICADOR <sent_post_punto>
```

---

### 3.7 Estructura condicional — si / entonces / sino / fin_si

```bnf
<sent_si> ::= si <expresion> entonces
                <bloque>
              <rama_sino>
              fin_si

<rama_sino> ::= sino <bloque>
              | ε
```

---

### 3.8 Estructura de repetición — para / desde / hasta / paso / fin_para

```bnf
<sent_para> ::= para IDENTIFICADOR desde <expresion>
                  hasta <expresion>
                  <paso_opt>
                hacer
                  <bloque>
                fin_para

<paso_opt> ::= paso <expresion>
             | ε
```

---

### 3.9 Estructura de repetición — mientras / hacer / fin_mientras

```bnf
<sent_mientras> ::= mientras <expresion>
                    hacer
                      <bloque>
                    fin_mientras
```

---

### 3.10 Instrucción de retorno

```bnf
<sent_retornar> ::= retornar <expresion_opt>

<expresion_opt> ::= <expresion>
                  | ε
```

---

### 3.11 Llamada a función o método — argumentos

```bnf
<sufijo_llamada> ::= "(" <argumentos> ")"

<argumentos> ::= <arg_lista>
               | ε

<arg_lista>      ::= <expresion> <arg_lista_cont>
<arg_lista_cont> ::= "," <expresion> <arg_lista_cont>
                   | ε
```

---

### 3.12 Expresiones — jerarquía de precedencia con recursividad derecha

```
NIVEL 1 — disyuncion_logica          o         (menor precedencia)
NIVEL 2 — conjuncion_logica          y
NIVEL 3 — comparacion                == != < > <= >=
NIVEL 4 — suma_o_resta               + -
NIVEL 5 — multiplicacion_div_mod     * / %
NIVEL 6 — potencia                   ^
NIVEL 7 — operacion_unaria           no  -
NIVEL 8 — valor_atomico              literal / variable / llamada   (mayor precedencia)
```

```bnf
<expresion> ::= <disyuncion_logica>


/* NIVEL 1 — Disyunción lógica  (operador: o) */
<disyuncion_logica>       ::= <conjuncion_logica> <continuacion_disyuncion>
<continuacion_disyuncion> ::= o <conjuncion_logica> <continuacion_disyuncion>
                            | ε


/* NIVEL 2 — Conjunción lógica  (operador: y) */
<conjuncion_logica>       ::= <comparacion> <continuacion_conjuncion>
<continuacion_conjuncion> ::= y <comparacion> <continuacion_conjuncion>
                            | ε


/* NIVEL 3 — Comparación relacional e igualdad */
<comparacion>              ::= <suma_o_resta> <continuacion_comparacion>
<continuacion_comparacion> ::= <operador_comparacion> <suma_o_resta>
                             | ε

<operador_comparacion> ::= "==" | "!=" | "<" | ">" | "<=" | ">="


/* NIVEL 4 — Suma y resta  (operadores: + -) */
<suma_o_resta>            ::= <multiplicacion_div_mod> <continuacion_suma_resta>
<continuacion_suma_resta> ::= "+" <multiplicacion_div_mod> <continuacion_suma_resta>
                            | "-" <multiplicacion_div_mod> <continuacion_suma_resta>
                            | ε


/* NIVEL 5 — Multiplicación, división y módulo  (operadores: * / %) */
<multiplicacion_div_mod>   ::= <potencia> <continuacion_mul_div_mod>
<continuacion_mul_div_mod> ::= "*" <potencia> <continuacion_mul_div_mod>
                             | "/" <potencia> <continuacion_mul_div_mod>
                             | "%" <potencia> <continuacion_mul_div_mod>
                             | ε


/* NIVEL 6 — Potencia  (operador: ^) */
<potencia>              ::= <operacion_unaria> <continuacion_potencia>
<continuacion_potencia> ::= "^" <operacion_unaria> <continuacion_potencia>
                          | ε


/* NIVEL 7 — Operación unaria  (operadores: no  -) */
<operacion_unaria> ::= no <operacion_unaria>
                     | "-" <operacion_unaria>
                     | <valor_atomico>


/* NIVEL 8 — Valor atómico */
<valor_atomico> ::= NUMERO_ENTERO
                  | NUMERO_REAL
                  | CADENA_LITERAL
                  | verdadero
                  | falso
                  | nulo
                  | nuevo IDENTIFICADOR "(" <argumentos> ")"
                  | este "." IDENTIFICADOR <sufijo_valor_atomico>
                  | IDENTIFICADOR <sufijo_valor_atomico>
                  | "(" <expresion> ")"

<sufijo_valor_atomico> ::= "(" <argumentos> ")" <acceso_encadenado_opt>
                         | "." IDENTIFICADOR <sufijo_valor_atomico>
                         | ε

<acceso_encadenado_opt> ::= "." IDENTIFICADOR <sufijo_valor_atomico>
                          | ε
```

---

### 3.13 Tipos

```bnf
<tipo> ::= entero
         | real
         | cadena
         | booleano
         | IDENTIFICADOR
```

---

## 4. Tabla de conjuntos FIRST y FOLLOW

### 4.1 FIRST de no-terminales clave

| No-terminal | FIRST |
|---|---|
| `<programa>` | `{ clase, funcion, var, si, para, mientras, este, IDENT, ε }` |
| `<declaracion>` | `{ clase, funcion, var, si, para, mientras, este, IDENT }` |
| `<def_clase>` | `{ clase }` |
| `<def_funcion>` | `{ funcion }` |
| `<lista_miembros>` | `{ publico, privado, funcion, IDENT, ε }` |
| `<miembro>` | `{ publico, privado, funcion, IDENT }` |
| `<miembro_base>` | `{ funcion, IDENT }` |
| `<modificador>` | `{ publico, privado, ε }` |
| `<bloque>` | `{ var, si, para, mientras, retornar, este, IDENT }` |
| `<sentencia_no_retorno_seq>` | `{ var, si, para, mientras, este, IDENT, ε }` |
| `<retorno_final_opt>` | `{ retornar, ε }` |
| `<sentencia>` | `{ var, si, para, mientras, retornar, este, IDENT }` |
| `<sentencia_no_retorno>` | `{ var, si, para, mientras, este, IDENT }` |
| `<decl_variable>` | `{ var }` |
| `<sent_si>` | `{ si }` |
| `<sent_para>` | `{ para }` |
| `<sent_mientras>` | `{ mientras }` |
| `<sent_retornar>` | `{ retornar }` |
| `<sent_identificador>` | `{ este, IDENT }` |
| `<sent_identificador_cont>` | `{ =, (, . }` |
| `<sent_post_punto>` | `{ =, (, . }` |
| `<expresion_opt>` | `{ NUMERO_ENTERO, NUMERO_REAL, CADENA_LITERAL, verdadero, falso, nulo, nuevo, este, IDENT, (, no, -, ε }` |
| `<expresion>` | `{ NUMERO_ENTERO, NUMERO_REAL, CADENA_LITERAL, verdadero, falso, nulo, nuevo, este, IDENT, (, no, - }` |
| `<rama_sino>` | `{ sino, ε }` |
| `<paso_opt>` | `{ paso, ε }` |
| `<inicializacion_opt>` | `{ =, ε }` |
| `<tipo_retorno_opt>` | `{ :, ε }` |
| `<herencia_opt>` | `{ extiende, ε }` |
| `<parametros>` | `{ IDENT, ε }` |
| `<argumentos>` | `{ NUMERO_ENTERO, NUMERO_REAL, CADENA_LITERAL, verdadero, falso, nulo, nuevo, este, IDENT, (, no, -, ε }` |
| `<tipo>` | `{ entero, real, cadena, booleano, IDENT }` |

### 4.2 FOLLOW de no-terminales con producciones ε

| No-terminal | FOLLOW |
|---|---|
| `<programa>` | `{ $ }` |
| `<lista_miembros>` | `{ fin_clase }` |
| `<sentencia_no_retorno_seq>` | `{ fin_funcion, fin_si, fin_para, fin_mientras, sino, retornar }` |
| `<retorno_final_opt>` | `{ fin_funcion, fin_si, fin_para, fin_mientras, sino }` |
| `<expresion_opt>` | `{ fin_funcion, fin_si, fin_para, fin_mientras, sino }` |
| `<rama_sino>` | `{ fin_si }` |
| `<paso_opt>` | `{ hacer }` |
| `<inicializacion_opt>` | `{ $, var, si, para, mientras, retornar, este, IDENT, publico, privado, funcion, fin_clase, fin_funcion, fin_si, fin_para, fin_mientras, sino }` |
| `<tipo_retorno_opt>` | `{ var, si, para, mientras, retornar, este, IDENT }` |
| `<herencia_opt>` | `{ publico, privado, funcion, IDENT, fin_clase }` |
| `<modificador>` | `{ funcion, IDENT }` |
| `<parametros>` | `{ ) }` |
| `<param_lista_cont>` | `{ ) }` |
| `<argumentos>` | `{ ) }` |
| `<arg_lista_cont>` | `{ ) }` |
| `<sufijo_valor_atomico>` | (depende del contexto — ver expresiones) |
| `<acceso_encadenado_opt>` | (depende del contexto — ver expresiones) |
| `<continuacion_disyuncion>` | `{ entonces, hacer, fin_si, fin_para, fin_mientras, fin_funcion, sino, ), ,, $ }` |
| `<continuacion_conjuncion>` | `{ o } ∪ FOLLOW(<continuacion_disyuncion>)` |
| `<continuacion_comparacion>` | `{ y } ∪ FOLLOW(<continuacion_conjuncion>)` |
| `<continuacion_suma_resta>` | `{ ==, !=, <, >, <=, >= } ∪ FOLLOW(<continuacion_comparacion>)` |
| `<continuacion_mul_div_mod>` | `{ +, - } ∪ FOLLOW(<continuacion_suma_resta>)` |
| `<continuacion_potencia>` | `{ *, /, % } ∪ FOLLOW(<continuacion_mul_div_mod>)` |

---

## 5. Verificación de condición LL(1)

### 5.1 Sin recursividad izquierda

Todas las producciones recursivas usan el patrón `A → α A_cont` — el no-terminal recursivo
aparece al **final**, nunca al inicio. La expansión de `*` y `+` en la Entrega 2 mantiene
esta propiedad:

```
<programa>                 ::= <declaracion> <programa> | ε
<lista_miembros>           ::= <miembro> <lista_miembros> | ε
<sentencia_no_retorno_seq> ::= <sentencia_no_retorno> <sentencia_no_retorno_seq> | ε
<continuacion_suma_resta>  ::= "+" <multiplicacion_div_mod> <continuacion_suma_resta> | ε
```

### 5.2 FIRST disjuntos en todas las alternativas

Tras las correcciones finales de implementación, los puntos sensibles quedan resueltos así:

| No-terminal corregido | FIRST alt.1 | FIRST alt.2 | FIRST alt.3 | ¿Disjuntos? |
|---|---|---|---|---|
| `<miembro_base>` | `{ funcion }` | `{ IDENT }` | — | ✓ |
| `<sent_identificador>` | `{ IDENT }` | `{ este }` | — | ✓ |
| `<sent_identificador_cont>` | `{ = }` | `{ ( }` | `{ . }` | ✓ |
| `<sent_post_punto>` | `{ = }` | `{ ( }` | `{ . }` | ✓ |
| `<retorno_final_opt>` | `{ retornar }` | `{ fin_funcion, fin_si, fin_para, fin_mientras, sino }` | — | ✓ |
| `<sentencia_no_retorno_seq>` | FIRST(`<sentencia_no_retorno>`) | FOLLOW(`<sentencia_no_retorno_seq>`) | — | ✓ |
| `<programa>` | FIRST(`<declaracion>`) | `{ $ }` | — | ✓ |
| `<lista_miembros>` | FIRST(`<miembro>`) | `{ fin_clase }` | — | ✓ |

### 5.3 Producciones ε controladas

Para cada no-terminal que deriva en ε, FIRST de la alternativa no vacía y FOLLOW del
no-terminal son disjuntos:

| No-terminal | FIRST (alt. no vacía) | FOLLOW | ¿Disjuntos? |
|---|---|---|---|
| `<programa>` | `{ clase, funcion, var, si, para, mientras, este, IDENT }` | `{ $ }` | ✓ |
| `<lista_miembros>` | `{ publico, privado, funcion, IDENT }` | `{ fin_clase }` | ✓ |
| `<sentencia_no_retorno_seq>` | `{ var, si, para, mientras, este, IDENT }` | `{ fin_funcion, fin_si, fin_para, fin_mientras, sino, retornar }` | ✓ |
| `<retorno_final_opt>` | `{ retornar }` | `{ fin_funcion, fin_si, fin_para, fin_mientras, sino }` | ✓ |
| `<expresion_opt>` | FIRST(`<expresion>`) | `{ fin_funcion, fin_si, fin_para, fin_mientras, sino }` | ✓ |
| `<rama_sino>` | `{ sino }` | `{ fin_si }` | ✓ |
| `<paso_opt>` | `{ paso }` | `{ hacer }` | ✓ |
| `<herencia_opt>` | `{ extiende }` | `{ publico, privado, funcion, IDENT, fin_clase }` | ✓ |
| `<tipo_retorno_opt>` | `{ : }` | `{ var, si, para, mientras, retornar, este, IDENT }` | ✓ |
| `<inicializacion_opt>` | `{ = }` | `{ $, var, si, para, mientras, retornar, este, IDENT, ... }` | ✓ |
| `<modificador>` | `{ publico, privado }` | `{ funcion, IDENT }` | ✓ |
| `<parametros>` | `{ IDENT }` | `{ ) }` | ✓ |
| `<argumentos>` | FIRST(`<expresion>`) | `{ ) }` | ✓ |

---

## 6. Ejemplos de programas válidos

### 6.1 Factorial recursivo

```
funcion factorial(n: entero): entero
  si n == 0 entonces
    retornar 1
  sino
    retornar n * factorial(n - 1)
  fin_si
fin_funcion

var resultado: entero = factorial(5)
```

### 6.2 Búsqueda lineal

```
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
```

### 6.3 Clase con atributos y métodos

```
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
```

### 6.4 Retornar sin expresión

```
funcion saludar()
  retornar
fin_funcion
```

---

## 7. Ejemplos de programas inválidos

### 7.1 Error sintáctico — falta `fin_si`

```
si x > 0 entonces
  var y: entero = 1
```

### 7.2 Error sintáctico — variable sin tipo explícito

```
var z = 5
```

### 7.3 Error sintáctico — operador lógico incorrecto

```
si x > 0 && y > 0 entonces
  retornar verdadero
fin_si
```

### 7.4 Error sintáctico — potencia con símbolo incorrecto

```
var resultado: real = 2 ** 8
```

---

## 8. Ajustes a la gramática de la Entrega 1

| # | Sección | Cambio | Motivo |
|---|---|---|---|
| 1 | §3.1 | `<declaracion>*` → `<programa> ::= <declaracion> <programa> \| ε` | Expandir EBNF a BNF pura |
| 2 | §3.2 | `<miembro>*` → `<lista_miembros>` con recursividad derecha | Expandir EBNF a BNF pura |
| 3 | §3.2 | `<miembro>` → `<modificador> <miembro_base>` | Hacer explícita la decisión LL(1) tras `publico` / `privado` |
| 4 | §3.4 | `<bloque>` reescrito con `<sentencia_no_retorno_seq>` y `<retorno_final_opt>` | Evitar conflicto FIRST/FOLLOW en `retornar` |
| 5 | §3.6 | `<sent_identificador>` ampliado para iniciar también con `este` | Soportar asignaciones y llamadas a miembros como `este.x = ...` |
| 6 | §3.6 | Factorización de `<sent_identificador_cont>` y nuevo `<sent_post_punto>` | Eliminar necesidad de lookahead k=2 |
| 7 | §4 | Tabla completa de FIRST y FOLLOW actualizada con los nuevos no-terminales | Requisito explícito del enunciado (E2) |
| 8 | §5 | Verificación LL(1) ajustada a la gramática realmente implementada | Coherencia entre documento y código |