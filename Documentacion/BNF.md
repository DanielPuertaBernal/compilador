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
- **Comentarios:** de línea con `//` y de bloque con `/* … */` (ignorados por el analizador).
- **Sensibilidad a mayúsculas:** el lenguaje distingue entre mayúsculas y minúsculas en identificadores.

---

## 2. Conjunto de terminales

### Palabras reservadas

```
var        funcion    retornar   clase      nuevo      este
extiende   publico    privado    si         entonces   sino
fin_si     para       desde      hasta      paso       hacer
fin_para   mientras   fin_mientras  fin_funcion  fin_clase
entero     real       cadena     booleano   nulo
verdadero  falso      y          o          no
```

### Operadores

```
+   -   *   /   %   ^        /* aritméticos */
==  !=  <   >   <=  >=       /* relacionales */
=                            /* asignación   */
```

### Delimitadores

```
(   )   ,   :   "   .
```

### Tokens léxicos

Los siguientes son **tokens terminales** producidos por el analizador léxico. No se expanden
en la gramática sintáctica — el parser los consume como unidades atómicas. Sus formas están
definidas por las siguientes expresiones regulares:

| Token | Expresión regular | Ejemplo |
|---|---|---|
| `IDENTIFICADOR` | `letra (letra \| dígito \| '_')*` | `miVariable`, `calcularÁrea`, `nombreñ` |
| `NUMERO_ENTERO` | `dígito+` | `0`, `42`, `1000` |
| `NUMERO_REAL` | `dígito+ '.' dígito+` | `3.14`, `0.5`, `100.0` |
| `CADENA_LITERAL` | `'"' (cualquier_carácter)* '"'` | `"Hola"`, `"mundo"` |

Donde:
- `letra` = `[a-z] | [A-Z] | [á-ú] | [Á-Ú] | ñ | Ñ`
- `dígito` = `[0-9]`
- `cualquier_carácter` = cualquier carácter Unicode excepto `"` sin escapar

> **Nota:** Las tildes (á, é, í, ó, ú) y la letra ñ/Ñ son válidas en identificadores,
> conforme al requisito 1 del enunciado. Las palabras reservadas **nunca** son identificadores
> válidos aunque coincidan léxicamente.

---

## 3. Producciones BNF

> **Convenciones:**
> - `e` representa la producción vacía (épsilon).
> - Los terminales se escriben en `"comillas"` o en **negrita** cuando son palabras reservadas.
> - Los no-terminales se escriben entre `< >`.

---

### 3.1 Programa

```bnf
<programa> ::= <declaracion>*

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

<param_lista> ::= <param> <param_lista'>

<param_lista'> ::= "," <param> <param_lista'>
                 | e

<param> ::= <IDENTIFICADOR> ":" <tipo>
```

---

### 3.4 Bloque y sentencias

```bnf
<bloque> ::= <sentencia>+

<sentencia> ::= <decl_variable>
              | <asignacion>
              | <sent_si>
              | <sent_para>
              | <sent_mientras>
              | <sent_retornar>
              | <llamada_sentencia>
```

---

### 3.5 Declaración de variable

```bnf
<decl_variable> ::= var <IDENTIFICADOR> ":" <tipo> <inicializacion_opt>

<inicializacion_opt> ::= "=" <expresion>
                       | e
```

---

### 3.6 Asignación

```bnf
<asignacion> ::= <IDENTIFICADOR> <sufijo_acceso_opt> "=" <expresion>

<sufijo_acceso_opt> ::= "." <IDENTIFICADOR> <sufijo_acceso_opt>
                      | e
```

---

### 3.7 Estructura condicional

```bnf
<sent_si> ::= si <expresion> entonces
                <bloque>
              <rama_sino>
              fin_si

<rama_sino> ::= sino <bloque>
              | e
```

---

### 3.8 Estructura para (for)

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

### 3.9 Estructura mientras (while)

```bnf
<sent_mientras> ::= mientras <expresion>
                    hacer
                      <bloque>
                    fin_mientras
```

---

### 3.10 Retorno

```bnf
<sent_retornar> ::= retornar <expresion>
                  | retornar
```

---

### 3.11 Llamada a función / método como sentencia

```bnf
<llamada_sentencia> ::= <IDENTIFICADOR> <sufijo_llamada>

<sufijo_llamada> ::= "(" <argumentos> ")"
                   | "." <IDENTIFICADOR> "(" <argumentos> ")"

<argumentos> ::= <arg_lista>
               | e

<arg_lista> ::= <expresion> <arg_lista'>

<arg_lista'> ::= "," <expresion> <arg_lista'>
               | e
```

---

### 3.12 Expresiones (con eliminación de recursividad izquierda)

La jerarquía de precedencia de menor a mayor es:
`or → and → relacional → suma/resta → multiplicación/división/módulo → potencia → unaria → primaria`

```bnf
<expresion> ::= <expr_or>

/* Disyunción lógica */
<expr_or>  ::= <expr_and> <expr_or'>
<expr_or'> ::= o <expr_and> <expr_or'>
             | e

/* Conjunción lógica */
<expr_and>  ::= <expr_rel> <expr_and'>
<expr_and'> ::= y <expr_rel> <expr_and'>
              | e

/* Relacionales */
<expr_rel>  ::= <expr_add> <expr_rel'>
<expr_rel'> ::= <op_rel> <expr_add>
              | e

<op_rel> ::= "==" | "!=" | "<" | ">" | "<=" | ">="

/* Suma y resta */
<expr_add>  ::= <expr_mul> <expr_add'>
<expr_add'> ::= "+" <expr_mul> <expr_add'>
              | "-" <expr_mul> <expr_add'>
              | e

/* Multiplicación, división y módulo */
<expr_mul>  ::= <expr_pot> <expr_mul'>
<expr_mul'> ::= "*" <expr_pot> <expr_mul'>
              | "/" <expr_pot> <expr_mul'>
              | "%" <expr_pot> <expr_mul'>
              | e

/* Potencia (asociatividad derecha — sin recursividad izquierda) */
<expr_pot> ::= <expr_unaria> <expr_pot'>
<expr_pot'> ::= "^" <expr_unaria> <expr_pot'>
              | e

/* Unaria */
<expr_unaria> ::= no <expr_unaria>
               | "-" <expr_unaria>
               | <expr_primaria>

/* Primaria */
<expr_primaria> ::= <NUMERO_ENTERO>
                  | <NUMERO_REAL>
                  | <CADENA_LITERAL>
                  | verdadero
                  | falso
                  | nulo
                  | nuevo <IDENTIFICADOR> "(" <argumentos> ")"
                  | este "." <IDENTIFICADOR> <sufijo_primaria>
                  | <IDENTIFICADOR> <sufijo_primaria>
                  | "(" <expresion> ")"

<sufijo_primaria> ::= "(" <argumentos> ")" <acceso_opt>
                    | "." <IDENTIFICADOR> <sufijo_primaria>
                    | e

<acceso_opt> ::= "." <IDENTIFICADOR> <sufijo_primaria>
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

> El último caso (`<IDENTIFICADOR>`) permite usar clases definidas por el usuario como tipo,
> por ejemplo: `var miAnimal: Animal`.

---

## 4. Verificación de condición LL

La gramática satisface la condición LL(1) / LL(k) porque:

1. **Sin recursividad izquierda:** todas las producciones recursivas usan la forma `A → α A'`
   con el no-terminal al final (recursividad derecha), nunca al inicio.
2. **Factorización aplicada:** los no-terminales con múltiples alternativas tienen conjuntos
   PRIMERO disjuntos. Por ejemplo:
   - `<sentencia>` se distingue por su token inicial: `var`, `si`, `para`, `mientras`,
     `retornar`, o `IDENTIFICADOR`.
   - `<expr_primaria>` se distingue por: `NUMERO_ENTERO`, `NUMERO_REAL`,
     `CADENA_LITERAL`, `verdadero`, `falso`, `nulo`, `nuevo`, `este`, `IDENTIFICADOR`, `(`.
3. **Producciones épsilon controladas:** los no-terminales que pueden derivar en `e`
   (`<rama_sino>`, `<paso_opt>`, `<parametros>`, etc.) tienen conjuntos SIGUIENTE
   disjuntos de los conjuntos PRIMERO de sus alternativas no vacías.

---

## 5. Ejemplos de programas

### 5.1 Factorial recursivo — demuestra funciones y retorno

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

### 5.2 Búsqueda lineal — demuestra `para`, `si` y variables

```
funcion buscar(valor: entero): booleano
  var encontrado: booleano = falso
  var lista: entero = 10

  para i desde 0 hasta lista paso 1 hacer
    si i == valor entonces
      encontrado = verdadero
    fin_si
  fin_para

  retornar encontrado
fin_funcion
```

### 5.3 Clase con atributos y métodos — demuestra OOP completo

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

## 6. Ejemplos de programas inválidos

### 6.1 Error: falta `fin_si`

```
// INVÁLIDO — bloque si sin cierre
si x > 0 entonces
  var y: entero = 1
```

### 6.2 Error: variable sin tipo

```
// INVÁLIDO — declaración sin tipo explícito
var z = 5
```

### 6.3 Error: operador lógico con símbolo en lugar de palabra

```
// INVÁLIDO — usar && en lugar de y
si x > 0 && y > 0 entonces
  retornar verdadero
fin_si
```

### 6.4 Error: potencia con símbolo incorrecto

```
// INVÁLIDO — usar ** en lugar de ^
var resultado: real = 2 ** 8
```