# Vocabulario del Lenguaje Fuente
**Compiladores — Entrega 1 | Lenguaje de destino: TypeScript**

---

## 1. Palabras Reservadas

### Tipos de datos

| Palabra reservada | Equivalente TypeScript |
|---|---|
| `entero` | `number` (entero) |
| `real` | `number` (flotante) |
| `cadena` | `string` |
| `booleano` | `boolean` |
| `nulo` | `null` |

### Clases

| Palabra reservada | Equivalente TypeScript |
|---|---|
| `clase` | `class` |
| `nuevo` | `new` |
| `este` | `this` |
| `extiende` | `extends` |
| `publico` | `public` |
| `privado` | `private` |

### Funciones

| Palabra reservada | Equivalente TypeScript |
|---|---|
| `funcion` | `function` |
| `retornar` | `return` |

### Estructuras de control

| Palabra reservada | Equivalente TypeScript |
|---|---|
| `si` | `if` |
| `entonces` | *(apertura del bloque if)* |
| `sino` | `else` |
| `fin_si` | `}` |
| `para` | `for` |
| `desde` | *(inicialización del for)* |
| `hasta` | *(condición del for)* |
| `paso` | *(incremento del for)* |
| `hacer` | *(apertura de bloque)* |
| `fin_para` | `}` |
| `mientras` | `while` |
| `fin_mientras` | `}` |
| `fin_funcion` | `}` |
| `fin_clase` | `}` |

### Operadores lógicos (palabras)

| Palabra reservada | Equivalente TypeScript |
|---|---|
| `y` | `&&` |
| `o` | `\|\|` |
| `no` | `!` |

### Literales booleanos

| Palabra reservada | Equivalente TypeScript |
|---|---|
| `verdadero` | `true` |
| `falso` | `false` |

### Declaración de variables

| Palabra reservada | Equivalente TypeScript |
|---|---|
| `var` | `let` |

---

## 2. Operadores

### Aritméticos (símbolos)

| Símbolo | Operación |
|---|---|
| `+` | Suma |
| `-` | Resta |
| `*` | Multiplicación |
| `/` | División |
| `%` | Módulo |
| `^` | Potencia |

### Relacionales (símbolos)

| Símbolo | Operación |
|---|---|
| `==` | Igual |
| `!=` | Distinto |
| `<` | Menor que |
| `>` | Mayor que |
| `<=` | Menor o igual |
| `>=` | Mayor o igual |

### Asignación

| Símbolo | Operación |
|---|---|
| `=` | Asignación |

---

## 3. Delimitadores

| Símbolo | Uso |
|---|---|
| `(` `)` | Parámetros y agrupación de expresiones |
| `,` | Separación de parámetros |
| `:` | Declaración de tipo (`var x: entero`) |
| `"` | Delimitador de cadenas de texto |
| `//` | Comentario de línea |
| `/* */` | Comentario de bloque |

---

## 4. Ejemplo de programa válido

```
// Declaración de variables
var contador: entero = 0
var nombre: cadena = "Hola"
var activo: booleano = verdadero

// Estructura para (desde / hasta / paso)
para i desde 0 hasta 10 paso 1 hacer
  var x: entero = i * 2
fin_para

// Clase con métodos usando funcion
clase Animal
  privado nombre: cadena
  privado edad: entero

  funcion constructor(n: cadena, e: entero)
    este.nombre = n
    este.edad = e
  fin_funcion

  funcion obtenerNombre(): cadena
    retornar este.nombre
  fin_funcion

  funcion esMayor(otraEdad: entero): booleano
    si este.edad > otraEdad entonces
      retornar verdadero
    sino
      retornar falso
    fin_si
  fin_funcion

fin_clase

// Instanciar y usar
var miAnimal: Animal = nuevo Animal("León", 5)
var resultado: booleano = miAnimal.esMayor(3)

// Clase con funcion que usa estructura para
clase Calculadora
  funcion sumarRango(inicio: entero, fin: entero): entero
    var total: entero = 0
    para i desde inicio hasta fin paso 1 hacer
      total = total + i
    fin_para
    retornar total
  fin_funcion
fin_clase
```