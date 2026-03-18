# Gramática Libre de Contexto — Notación BNF
**Compiladores — Entrega 1 | Lenguaje de destino: TypeScript**

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

Los siguientes son **tokens terminales** producidos por el analizador léxico. No se expanden
en la gramática sintáctica — el parser los consume como unidades atómicas. Sus formas están
definidas por las siguientes expresiones regulares:

| Token | Expresión regular | Ejemplo |
|---|---|---|
| `IDENTIFICADOR` | `letra (letra \| digito)*` | `miVariable`, `calcularÁrea`, `añoNacimiento` |
| `NUMERO_ENTERO` | `digito+` | `0`, `42`, `1000` |
| `NUMERO_REAL` | `digito+ '.' digito+` | `3.14`, `0.5`, `100.0` |
| `CADENA_LITERAL` | `'"' (cualquier_carácter)* '"'` | `"Hola"`, `"mundo"` |

Donde:
- `letra` = `[a-z] | [A-Z] | [á-ú] | [Á-Ú] | ñ | Ñ`
- `digito` = `[0-9]`
- `cualquier_carácter` = cualquier carácter Unicode excepto `"` sin escapar

> **Nota:** Las tildes (á, é, í, ó, ú) y la letra ñ/Ñ son válidas en identificadores,
> conforme al requisito 1 del enunciado. Las palabras reservadas **nunca** son identificadores
> válidos aunque coincidan léxicamente.

---

## 3. Producciones BNF

> **Convenciones:**
> - `e` representa la producción vacía (épsilon).
> - Los terminales aparecen entre `"comillas"` o como palabras reservadas en español.
> - Los no-terminales se escriben entre `< >`.
> - El patrón `<continuacion_X>` captura repetición del nivel X sin recursividad izquierda.

---

### 3.1 Programa

```bnf
<programa>    ::= <declaracion>*

<declaracion> ::= <def_clase>
               | <def_funcion>
               | <sentencia>
```

---

### 3.2 Definición de clase

```bnf
<def_clase> ::= clase <IDENTIFICADOR> <herencia_opt>
                  <miembro>*
                fin_clase

<herencia_opt> ::= extiende <IDENTIFICADOR>
                 | e

<miembro> ::= <modificador> <def_funcion>
            | <modificador> <decl_atributo>

<modificador> ::= publico
               | privado
               | e

<decl_atributo> ::= <IDENTIFICADOR> ":" <tipo>
                  | <IDENTIFICADOR> ":" <tipo> "=" <expresion>
```

---

### 3.3 Definición de función / método

```bnf
<def_funcion> ::= funcion <IDENTIFICADOR> "(" <parametros> ")" <tipo_retorno_opt>
                    <bloque>
                  fin_funcion

<tipo_retorno_opt> ::= ":" <tipo>
                     | e

<parametros> ::= <param_lista>
               | e

<param_lista>  ::= <param> <param_lista_cont>
<param_lista_cont> ::= "," <param> <param_lista_cont>
                     | e

<param> ::= <IDENTIFICADOR> ":" <tipo>
```

---

### 3.4 Bloque y sentencias

```bnf
<bloque> ::= <sentencia>+

<sentencia> ::= <decl_variable>
              | <sent_si>
              | <sent_para>
              | <sent_mientras>
              | <sent_retornar>
              | <sent_identificador>
```

> **Factorización aplicada:** asignación y llamada a función/método comparten el prefijo
> `IDENTIFICADOR`. Se fusionan en `<sent_identificador>` para cumplir LL(1). El parser
> decide cuál es después de consumir el identificador, mirando el token siguiente.

---

### 3.5 Declaración de variable

```bnf
<decl_variable> ::= var <IDENTIFICADOR> ":" <tipo> <inicializacion_opt>

<inicializacion_opt> ::= "=" <expresion>
                       | e
```

---

### 3.6 Sentencia iniciada por identificador — asignación o llamada

```bnf
<sent_identificador>  ::= <IDENTIFICADOR> <sent_identificador_cont>

<sent_identificador_cont> ::= <acceso_miembro_opt> "=" <expresion>   /* asignación */
                            | <sufijo_llamada>                         /* llamada a función */

<acceso_miembro_opt> ::= "." <IDENTIFICADOR> <acceso_miembro_opt>
                       | e
```

> **Decisión con lookahead k=2:** tras consumir `IDENTIFICADOR`, el parser inspecciona
> el siguiente token:
> - `"="` o `"."` seguido de más accesos → **asignación**
> - `"("` → **llamada a función o método**

---

### 3.7 Estructura condicional — si / entonces / sino / fin_si

```bnf
<sent_si> ::= si <expresion> entonces
                <bloque>
              <rama_sino>
              fin_si

<rama_sino> ::= sino <bloque>
              | e
```

---

### 3.8 Estructura de repetición — para / desde / hasta / paso / fin_para

```bnf
<sent_para> ::= para <IDENTIFICADOR> desde <expresion>
                  hasta <expresion>
                  <paso_opt>
                hacer
                  <bloque>
                fin_para

<paso_opt> ::= paso <expresion>
             | e
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
<sent_retornar> ::= retornar <expresion>
                  | retornar
```

---

### 3.11 Llamada a función o método — argumentos

```bnf
<sufijo_llamada> ::= "(" <argumentos> ")"
                   | "." <IDENTIFICADOR> "(" <argumentos> ")"

<argumentos> ::= <arg_lista>
               | e

<arg_lista>      ::= <expresion> <arg_lista_cont>
<arg_lista_cont> ::= "," <expresion> <arg_lista_cont>
                   | e
```

---

### 3.12 Expresiones — jerarquía de precedencia con recursividad derecha

La precedencia va de **menor a mayor**. Lo que está más abajo en la jerarquía se evalúa primero:

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

> **Patrón aplicado en cada nivel:**
> `<nivel> ::= <nivel_superior> <continuacion_nivel>`
> La `<continuacion_*>` permite repetir operadores del mismo nivel sin recursividad izquierda.

```bnf
<expresion> ::= <disyuncion_logica>


/* ══════════════════════════════════════════════════════════════
   NIVEL 1 — Disyunción lógica  (operador: o)
   Ejemplo:  activo o forzado o debug
   Es la de menor precedencia: se evalúa después de todo lo demás.
   ══════════════════════════════════════════════════════════════ */
<disyuncion_logica>       ::= <conjuncion_logica> <continuacion_disyuncion>
<continuacion_disyuncion> ::= o <conjuncion_logica> <continuacion_disyuncion>
                            | e


/* ══════════════════════════════════════════════════════════════
   NIVEL 2 — Conjunción lógica  (operador: y)
   Ejemplo:  mayor y activo y valido
   Se evalúa antes que la disyunción (mayor precedencia que o).
   ══════════════════════════════════════════════════════════════ */
<conjuncion_logica>       ::= <comparacion> <continuacion_conjuncion>
<continuacion_conjuncion> ::= y <comparacion> <continuacion_conjuncion>
                            | e


/* ══════════════════════════════════════════════════════════════
   NIVEL 3 — Comparación relacional e igualdad
   Ejemplo:  edad >= 18,  nombre == "Ana",  x != y
   Produce un booleano comparando dos valores numéricos o de texto.
   ══════════════════════════════════════════════════════════════ */
<comparacion>               ::= <suma_o_resta> <continuacion_comparacion>
<continuacion_comparacion>  ::= <operador_comparacion> <suma_o_resta>
                              | e

<operador_comparacion> ::= "==" | "!=" | "<" | ">" | "<=" | ">="


/* ══════════════════════════════════════════════════════════════
   NIVEL 4 — Suma y resta  (operadores: +  -)
   Ejemplo:  precio + impuesto - descuento
   ══════════════════════════════════════════════════════════════ */
<suma_o_resta>            ::= <multiplicacion_div_mod> <continuacion_suma_resta>
<continuacion_suma_resta> ::= "+" <multiplicacion_div_mod> <continuacion_suma_resta>
                            | "-" <multiplicacion_div_mod> <continuacion_suma_resta>
                            | e


/* ══════════════════════════════════════════════════════════════
   NIVEL 5 — Multiplicación, división y módulo  (operadores: *  /  %)
   Ejemplo:  ancho * alto,  total / cantidad,  indice % tamanio
   Se evalúa antes que suma y resta.
   ══════════════════════════════════════════════════════════════ */
<multiplicacion_div_mod>      ::= <potencia> <continuacion_mul_div_mod>
<continuacion_mul_div_mod>    ::= "*" <potencia> <continuacion_mul_div_mod>
                                | "/" <potencia> <continuacion_mul_div_mod>
                                | "%" <potencia> <continuacion_mul_div_mod>
                                | e


/* ══════════════════════════════════════════════════════════════
   NIVEL 6 — Potencia  (operador: ^)
   Ejemplo:  base ^ exponente,  2 ^ 8,  x ^ 0.5
   Asociatividad derecha: 2 ^ 3 ^ 2  =  2 ^ (3 ^ 2)  =  512
   ══════════════════════════════════════════════════════════════ */
<potencia>              ::= <operacion_unaria> <continuacion_potencia>
<continuacion_potencia> ::= "^" <operacion_unaria> <continuacion_potencia>
                          | e


/* ══════════════════════════════════════════════════════════════
   NIVEL 7 — Operación unaria  (operadores: no  -)
   Ejemplo:  no activo,  -saldo,  no (x > 0)
   Se aplica sobre un solo operando; no necesita continuación.
   ══════════════════════════════════════════════════════════════ */
<operacion_unaria> ::= no <operacion_unaria>
                     | "-" <operacion_unaria>
                     | <valor_atomico>


/* ══════════════════════════════════════════════════════════════
   NIVEL 8 — Valor atómico  (mayor precedencia — se evalúa primero)
   Son los valores que no se pueden descomponer más:
   literales, variables, llamadas a función, instanciación de clases
   y subexpresiones agrupadas entre paréntesis.
   ══════════════════════════════════════════════════════════════ */
<valor_atomico> ::= <NUMERO_ENTERO>
                  | <NUMERO_REAL>
                  | <CADENA_LITERAL>
                  | verdadero
                  | falso
                  | nulo
                  | nuevo <IDENTIFICADOR> "(" <argumentos> ")"
                  | este "." <IDENTIFICADOR> <sufijo_valor_atomico>
                  | <IDENTIFICADOR> <sufijo_valor_atomico>
                  | "(" <expresion> ")"

/* Sufijo: llamada a función o acceso encadenado a miembro */
<sufijo_valor_atomico> ::= "(" <argumentos> ")" <acceso_encadenado_opt>
                         | "." <IDENTIFICADOR> <sufijo_valor_atomico>
                         | e

/* Acceso encadenado tras una llamada: ej. objeto.metodo().atributo */
<acceso_encadenado_opt> ::= "." <IDENTIFICADOR> <sufijo_valor_atomico>
                          | e
```

---

### 3.13 Tipos

```bnf
<tipo> ::= entero
         | real
         | cadena
         | booleano
         | <IDENTIFICADOR>
```

> El caso `<IDENTIFICADOR>` permite usar clases propias como tipo:
> `var miAnimal: Animal` o `var r: Rectangulo`.

---

## 4. Cobertura de capacidades mínimas exigidas

La siguiente tabla evidencia que la gramática cubre los 10 requisitos del enunciado sin excepción:

| # | Capacidad exigida | Producción / terminal BNF |
|---|---|---|
| 1 | Palabras reservadas e identificadores en español (tildes, ñ) | Sección 2.1 y token `IDENTIFICADOR` con `letra = [a-z\|A-Z\|á-ú\|Á-Ú\|ñ\|Ñ]` |
| 2 | Operaciones aritméticas: `+`, `-`, `*`, `/`, `%`, `^` | `<suma_o_resta>`, `<multiplicacion_div_mod>`, `<potencia>` |
| 3 | Operaciones lógicas: `y`, `o`, `no` | `<disyuncion_logica>`, `<conjuncion_logica>`, `<operacion_unaria>` |
| 4 | Operaciones relacionales: `==`, `!=`, `<`, `>`, `<=`, `>=` | `<comparacion>`, `<operador_comparacion>` |
| 5 | Condicional `si … entonces … sino … fin_si` | `<sent_si>`, `<rama_sino>` |
| 6 | Repetición `para … desde … hasta … paso … hacer … fin_para` | `<sent_para>`, `<paso_opt>` |
| 7 | Repetición `mientras … hacer … fin_mientras` | `<sent_mientras>` |
| 8 | Definición de clases con atributos y métodos | `<def_clase>`, `<miembro>`, `<modificador>`, `<decl_atributo>`, `<def_funcion>` |
| 9 | Tipos básicos: `entero`, `real`, `cadena`, `booleano` | `<tipo>`, tokens `NUMERO_ENTERO`, `NUMERO_REAL`, `CADENA_LITERAL`, `verdadero`, `falso` |
| 10 | Asignación y `retornar` | `<sent_identificador_cont>` rama asignación, `<sent_retornar>` |

---

## 5. Verificación de condición LL

La gramática satisface la condición LL(1) / LL(k) por las siguientes razones:

### 5.1 Sin recursividad izquierda

Todas las producciones recursivas usan el patrón `A → α A_cont` — el no-terminal recursivo
aparece al **final**, nunca al inicio. Ejemplos:

```
<continuacion_suma_resta>  ::= "+" <multiplicacion_div_mod> <continuacion_suma_resta> | e
<param_lista_cont>         ::= "," <param> <param_lista_cont>                         | e
<arg_lista_cont>           ::= "," <expresion> <arg_lista_cont>                       | e
```

### 5.2 Factorización por prefijos comunes

El único caso de prefijo compartido es `IDENTIFICADOR` en `<sentencia>`, que puede iniciar
tanto una asignación como una llamada. Se resuelve fusionándolas en `<sent_identificador>`:

```
<sent_identificador>      ::= <IDENTIFICADOR> <sent_identificador_cont>
<sent_identificador_cont> ::= <acceso_miembro_opt> "=" <expresion>   /* asignación */
                            | <sufijo_llamada>                         /* llamada    */
```

Tras consumir `IDENTIFICADOR`, el parser inspecciona el siguiente token:
`"="` o `"."` → asignación · `"("` → llamada.

### 5.3 Conjuntos PRIMERO — no-terminales críticos

```
PRIMERO(<declaracion>)            = { clase, funcion, var, si, para, mientras, retornar, IDENT }

PRIMERO(<sentencia>)              = { var, si, para, mientras, retornar, IDENT }
  var       →  <decl_variable>
  si        →  <sent_si>
  para      →  <sent_para>
  mientras  →  <sent_mientras>
  retornar  →  <sent_retornar>
  IDENT     →  <sent_identificador>   ← único caso compartido, resuelto por factorización

PRIMERO(<sent_identificador_cont>) = { "=", ".", "(" }              ← disjuntos entre sí

PRIMERO(<valor_atomico>)          = { NUMERO_ENTERO, NUMERO_REAL, CADENA_LITERAL,
                                      verdadero, falso, nulo, nuevo, este, IDENT, "(" }

PRIMERO(<disyuncion_logica>)      = PRIMERO(<valor_atomico>) ∪ { no, "-" }
PRIMERO(<conjuncion_logica>)      = PRIMERO(<valor_atomico>) ∪ { no, "-" }
PRIMERO(<comparacion>)            = PRIMERO(<valor_atomico>) ∪ { no, "-" }
PRIMERO(<suma_o_resta>)           = PRIMERO(<valor_atomico>) ∪ { no, "-" }
PRIMERO(<multiplicacion_div_mod>) = PRIMERO(<valor_atomico>) ∪ { no, "-" }
PRIMERO(<potencia>)               = PRIMERO(<valor_atomico>) ∪ { no, "-" }
PRIMERO(<operacion_unaria>)       = PRIMERO(<valor_atomico>) ∪ { no, "-" }

PRIMERO(<tipo>)                   = { entero, real, cadena, booleano, IDENT }
PRIMERO(<miembro>)                = { publico, privado, funcion, IDENT }
```

### 5.4 Producciones épsilon controladas

Los no-terminales que derivan en `e` tienen conjuntos SIGUIENTE disjuntos de los PRIMERO
de sus alternativas no vacías — garantizando que el parser siempre sepa si expandir o no:

| No-terminal | PRIMERO (alternativa no vacía) | SIGUIENTE |
|---|---|---|
| `<rama_sino>` | `{ sino }` | `{ fin_si }` |
| `<paso_opt>` | `{ paso }` | `{ hacer }` |
| `<parametros>` | `{ IDENT }` | `{ ")" }` |
| `<inicializacion_opt>` | `{ "=" }` | `{ fin_funcion, fin_clase, var, si, para, ... }` |
| `<tipo_retorno_opt>` | `{ ":" }` | `{ var, si, para, mientras, retornar, IDENT }` |
| `<herencia_opt>` | `{ extiende }` | `{ publico, privado, funcion, IDENT }` |
| `<acceso_miembro_opt>` | `{ "." }` | `{ "=" }` |
| `<continuacion_disyuncion>` | `{ o }` | `{ entonces, hacer, fin_si, fin_para, fin_mientras, ")", "," }` |

---

## 6. Ejemplos de programas válidos

### 6.1 Factorial recursivo — funciones, condicional y retorno

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

### 6.2 Búsqueda lineal — para, si y variables

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

### 6.3 Clase con atributos y métodos — OOP completo

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

---

## 7. Ejemplos de programas inválidos

### 7.1 Error sintáctico — falta `fin_si`

```
// INVÁLIDO — bloque si sin cierre
si x > 0 entonces
  var y: entero = 1
```

### 7.2 Error sintáctico — variable sin tipo explícito

```
// INVÁLIDO — declaración sin tipo
var z = 5
```

### 7.3 Error sintáctico — operador lógico con símbolo en lugar de palabra

```
// INVÁLIDO — usar && en lugar de y
si x > 0 && y > 0 entonces
  retornar verdadero
fin_si
```

### 7.4 Error sintáctico — potencia con símbolo incorrecto

```
// INVÁLIDO — usar ** en lugar de ^
var resultado: real = 2 ** 8
```

---

## 8. Errores léxicos específicos

Los siguientes casos son detectados por el **analizador léxico**, no por el sintáctico.
El lexer debe reportar fila y columna del error y continuar analizando el resto de la cadena.

### 8.1 Carácter inválido

```
// INVÁLIDO — '@' no pertenece al alfabeto del lenguaje
var resultado: entero = 10 @ 2
```

> **Error léxico** — fila 2, columna 28: carácter `@` no reconocido.

### 8.2 Cadena de texto sin cerrar

```
// INVÁLIDO — la cadena no tiene comilla de cierre
var nombre: cadena = "Hola mundo
var edad: entero = 5
```

> **Error léxico** — fila 2, columna 22: fin de línea dentro de una cadena literal. Se esperaba `"`.

### 8.3 Comentario de bloque sin cerrar

```
/* Este comentario nunca cierra
var x: entero = 1
```

> **Error léxico** — fin de archivo: comentario de bloque abierto en fila 1, columna 1 sin `*/` de cierre.

### 8.4 Identificador con carácter inválido

```
// INVÁLIDO — '#' no es válido en un identificador
var mi#variable: entero = 0
```

> **Error léxico** — fila 2, columna 7: carácter `#` inesperado dentro de un identificador.