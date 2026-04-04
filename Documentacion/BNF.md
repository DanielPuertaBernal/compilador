# Gramática Libre de Contexto — Notación BNF
**Compiladores — Entrega 2 | Lenguaje de destino: TypeScript**

> **Nota de versión:** Este documento reemplaza la gramática de la Entrega 1.
> Se aplicaron tres correcciones necesarias para garantizar la condición LL(1) estricta
> requerida por el analizador sintáctico predictivo descendente:
>
> 1. Las notaciones EBNF `*` y `+` se expandieron a producciones BNF recursivas explícitas.
> 2. `<sent_retornar>` se refactorizó para eliminar ambigüedad en FIRST.
> 3. `<sent_identificador_cont>` se factorizó para tener FIRST disjuntos sin lookahead k=2.

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

> **Corrección aplicada (Alerta 1):** La notación EBNF `<declaracion>*` se expandió a
> recursividad derecha explícita. `<programa>` puede derivar en ε, permitiendo programas vacíos.

```bnf
<declaracion> ::= <def_clase>
               | <def_funcion>
               | <sentencia>
```

FIRST(`<declaracion>`) = `{ clase, funcion, var, si, para, mientras, retornar, IDENT }`  
FIRST(`ε`) se decide por SIGUIENTE(`<programa>`) = `{ $ }`  
→ Disjuntos. LL(1) correcto.

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

> **Corrección aplicada (Alerta 1):** La notación EBNF `<miembro>*` dentro de `<def_clase>`
> se expandió a `<lista_miembros>` con recursividad derecha explícita.

FIRST(`<miembro>`) = `{ publico, privado, funcion, IDENT }`  
SIGUIENTE(`<lista_miembros>`) = `{ fin_clase }`  
→ Disjuntos. LL(1) correcto.

```bnf
<miembro> ::= <modificador> <def_funcion>
            | <modificador> <decl_atributo>

<modificador> ::= publico
               | privado
               | ε

<decl_atributo> ::= IDENTIFICADOR ":" <tipo>
                  | IDENTIFICADOR ":" <tipo> "=" <expresion>
```

> **Nota:** `<decl_atributo>` comparte prefijo `IDENTIFICADOR ":" <tipo>`. Se factoriza:

```bnf
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
<bloque>      ::= <sentencia> <bloque_cont>
<bloque_cont> ::= <sentencia> <bloque_cont>
                | ε
```

> **Corrección aplicada (Alerta 1):** La notación EBNF `<sentencia>+` se expandió.
> `<bloque>` exige al menos una sentencia (la primera es obligatoria). `<bloque_cont>`
> maneja el resto con ε, preservando la semántica del operador `+`.

FIRST(`<sentencia>`) = `{ var, si, para, mientras, retornar, IDENT }`  
SIGUIENTE(`<bloque_cont>`) = `{ fin_funcion, fin_si, fin_para, fin_mientras, sino }`  
→ Disjuntos. LL(1) correcto.

```bnf
<sentencia> ::= <decl_variable>
              | <sent_si>
              | <sent_para>
              | <sent_mientras>
              | <sent_retornar>
              | <sent_identificador>
```

FIRST de cada alternativa:

| Alternativa | FIRST |
|---|---|
| `<decl_variable>` | `{ var }` |
| `<sent_si>` | `{ si }` |
| `<sent_para>` | `{ para }` |
| `<sent_mientras>` | `{ mientras }` |
| `<sent_retornar>` | `{ retornar }` |
| `<sent_identificador>` | `{ IDENT }` |

Todos disjuntos. LL(1) correcto.

---

### 3.5 Declaración de variable

```bnf
<decl_variable> ::= var IDENTIFICADOR ":" <tipo> <inicializacion_opt>

<inicializacion_opt> ::= "=" <expresion>
                       | ε
```

---

### 3.6 Sentencia iniciada por identificador — asignación o llamada

> **Corrección aplicada (Alerta 3 — lookahead k=2):**
>
> El problema original era que `<sent_identificador_cont>` tenía dos alternativas con
> FIRST no disjuntos: el punto `"."` aparecía tanto en el inicio del acceso a miembro
> (camino a asignación) como en el inicio de llamada a método.
>
> **Solución:** se factoriza el punto completamente, separando los tres caminos posibles
> (asignación directa, llamada a función, punto) en alternativas con FIRST disjuntos `{=}`,
> `{(}`, `{.}`. El caso del punto luego decide recursivamente si termina en asignación
> o en llamada a método.

```bnf
<sent_identificador> ::= IDENTIFICADOR <sent_identificador_cont>

<sent_identificador_cont> ::= "=" <expresion>
                            | "(" <argumentos> ")"
                            | "." IDENTIFICADOR <sent_post_punto>

<sent_post_punto> ::= "=" <expresion>
                    | "(" <argumentos> ")"
                    | "." IDENTIFICADOR <sent_post_punto>
```

FIRST de `<sent_identificador_cont>`:

| Alternativa | FIRST |
|---|---|
| `"=" <expresion>` | `{ = }` |
| `"(" <argumentos> ")"` | `{ ( }` |
| `"." IDENT <sent_post_punto>` | `{ . }` |

Todos disjuntos. LL(1) correcto, sin necesidad de lookahead k=2.

FIRST de `<sent_post_punto>`:

| Alternativa | FIRST |
|---|---|
| `"=" <expresion>` | `{ = }` |
| `"(" <argumentos> ")"` | `{ ( }` |
| `"." IDENT <sent_post_punto>` | `{ . }` |

Todos disjuntos. LL(1) correcto.

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

FIRST(`sino`) = `{ sino }`  
SIGUIENTE(`<rama_sino>`) = `{ fin_si }`  
→ Disjuntos. LL(1) correcto.

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

FIRST(`paso`) = `{ paso }`  
SIGUIENTE(`<paso_opt>`) = `{ hacer }`  
→ Disjuntos. LL(1) correcto.

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

> **Corrección aplicada (Alerta 2):**
>
> La gramática original tenía:
> ```
> <sent_retornar> ::= retornar <expresion>  |  retornar
> ```
> Ambas alternativas tienen FIRST = `{ retornar }`. La tabla LL(1) no puede decidir.
>
> **Solución:** se introduce `<expresion_opt>` para que el `retornar` solo aparezca una vez.

```bnf
<sent_retornar> ::= retornar <expresion_opt>

<expresion_opt> ::= <expresion>
                  | ε
```

FIRST(`<expresion>`) = `{ NUMERO_ENTERO, NUMERO_REAL, CADENA_LITERAL, verdadero, falso,`  
`  nulo, nuevo, este, IDENT, (, no, - }`  
SIGUIENTE(`<expresion_opt>`) = `{ fin_funcion, fin_si, fin_para, fin_mientras, sino, $ }`  
→ Disjuntos. LL(1) correcto.

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
| `<programa>` | `{ clase, funcion, var, si, para, mientras, retornar, IDENT, ε }` |
| `<declaracion>` | `{ clase, funcion, var, si, para, mientras, retornar, IDENT }` |
| `<def_clase>` | `{ clase }` |
| `<def_funcion>` | `{ funcion }` |
| `<lista_miembros>` | `{ publico, privado, funcion, IDENT, ε }` |
| `<miembro>` | `{ publico, privado, funcion, IDENT }` |
| `<modificador>` | `{ publico, privado, ε }` |
| `<bloque>` | `{ var, si, para, mientras, retornar, IDENT }` |
| `<bloque_cont>` | `{ var, si, para, mientras, retornar, IDENT, ε }` |
| `<sentencia>` | `{ var, si, para, mientras, retornar, IDENT }` |
| `<decl_variable>` | `{ var }` |
| `<sent_si>` | `{ si }` |
| `<sent_para>` | `{ para }` |
| `<sent_mientras>` | `{ mientras }` |
| `<sent_retornar>` | `{ retornar }` |
| `<sent_identificador>` | `{ IDENT }` |
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
| `<bloque_cont>` | `{ fin_funcion, fin_si, fin_para, fin_mientras, sino }` |
| `<expresion_opt>` | `{ fin_funcion, fin_si, fin_para, fin_mientras, sino, $ }` |
| `<rama_sino>` | `{ fin_si }` |
| `<paso_opt>` | `{ hacer }` |
| `<inicializacion_opt>` | `{ fin_funcion, fin_si, fin_para, fin_mientras, sino, var, si, para, mientras, retornar, IDENT, publico, privado, fin_clase }` |
| `<tipo_retorno_opt>` | `{ var, si, para, mientras, retornar, IDENT }` |
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
<programa>             ::= <declaracion> <programa> | ε
<lista_miembros>       ::= <miembro> <lista_miembros> | ε
<bloque_cont>          ::= <sentencia> <bloque_cont> | ε
<continuacion_suma_resta> ::= "+" <multiplicacion_div_mod> <continuacion_suma_resta> | ε
```

### 5.2 FIRST disjuntos en todas las alternativas

Tras las tres correcciones, ningún no-terminal presenta ambigüedad:

| No-terminal corregido | FIRST alt.1 | FIRST alt.2 | FIRST alt.3 | ¿Disjuntos? |
|---|---|---|---|---|
| `<sent_identificador_cont>` | `{ = }` | `{ ( }` | `{ . }` | ✓ |
| `<sent_post_punto>` | `{ = }` | `{ ( }` | `{ . }` | ✓ |
| `<sent_retornar>` | único camino con `<expresion_opt>` | — | — | ✓ |
| `<expresion_opt>` | FIRST(`<expresion>`) | FOLLOW(`<expresion_opt>`) | — | ✓ |
| `<bloque_cont>` | FIRST(`<sentencia>`) | FOLLOW(`<bloque_cont>`) | — | ✓ |
| `<programa>` | FIRST(`<declaracion>`) | `{ $ }` | — | ✓ |
| `<lista_miembros>` | FIRST(`<miembro>`) | `{ fin_clase }` | — | ✓ |

### 5.3 Producciones ε controladas

Para cada no-terminal que deriva en ε, FIRST de la alternativa no vacía y FOLLOW del
no-terminal son disjuntos:

| No-terminal | FIRST (alt. no vacía) | FOLLOW | ¿Disjuntos? |
|---|---|---|---|
| `<programa>` | `{ clase, funcion, var, si, para, ... }` | `{ $ }` | ✓ |
| `<lista_miembros>` | `{ publico, privado, funcion, IDENT }` | `{ fin_clase }` | ✓ |
| `<bloque_cont>` | `{ var, si, para, mientras, retornar, IDENT }` | `{ fin_funcion, fin_si, fin_para, fin_mientras, sino }` | ✓ |
| `<expresion_opt>` | FIRST(`<expresion>`) | `{ fin_funcion, fin_si, ... }` | ✓ |
| `<rama_sino>` | `{ sino }` | `{ fin_si }` | ✓ |
| `<paso_opt>` | `{ paso }` | `{ hacer }` | ✓ |
| `<herencia_opt>` | `{ extiende }` | `{ publico, privado, funcion, IDENT, fin_clase }` | ✓ |
| `<tipo_retorno_opt>` | `{ : }` | `{ var, si, para, mientras, retornar, IDENT }` | ✓ |
| `<inicializacion_opt>` | `{ = }` | `{ fin_funcion, fin_si, ... }` | ✓ |
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

### 6.4 retornar sin expresión (corrección Alerta 2)

```
funcion saludar()
  retornar
fin_funcion
```

> Este programa ahora es válido. Bajo la gramática corregida, `retornar` consume
> `<expresion_opt>` que deriva en ε al ver `fin_funcion` en el FOLLOW.

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

## 8. Registro de cambios respecto a la Entrega 1

| # | Sección | Cambio | Motivo |
|---|---|---|---|
| 1 | §3.1 | `<declaracion>*` → `<programa> ::= <declaracion> <programa> \| ε` | Alerta 1: expandir EBNF a BNF pura |
| 2 | §3.2 | `<miembro>*` → `<lista_miembros>` con recursividad derecha | Alerta 1: expandir EBNF a BNF pura |
| 3 | §3.4 | `<sentencia>+` → `<bloque> + <bloque_cont>` | Alerta 1: expandir EBNF a BNF pura |
| 4 | §3.6 | Factorización de `<sent_identificador_cont>` y nuevo `<sent_post_punto>` | Alerta 3: eliminar necesidad de lookahead k=2 |
| 5 | §3.10 | `retornar <expresion> \| retornar` → `retornar <expresion_opt>` | Alerta 2: eliminar ambigüedad de FIRST |
| 6 | §4 | Tabla completa de FIRST y FOLLOW añadida | Requisito explícito del enunciado (E2) |
| 7 | §5 | Verificación LL(1) actualizada con nuevas producciones | Coherencia con correcciones |