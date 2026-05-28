# Compilador Fuente-a-Fuente — Español a TypeScript
**Teoría de Compiladores — Trabajo de curso | Entregas 1, 2, 3 y 4**

Proyecto de curso para un lenguaje fuente con palabras reservadas en español, análisis léxico, sintáctico, recuperación de errores con sugerencias generadas por IA y análisis semántico con tabla de símbolos.

---

## Resumen del proyecto

- **Lenguaje fuente:** imperativo y orientado a objetos, sintaxis en español
- **Lenguaje destino:** TypeScript
- **Entrega 1:** analizador léxico con visualización interactiva
- **Entrega 2:** parser recursivo y predictivo LL(1) con árbol sintáctico
- **Entrega 3:** recuperación de errores en modo pánico + sugerencias con IA (Naive Bayes)
- **Entrega 4:** analizador semántico con tabla de símbolos, 5 reglas semánticas y detección de errores

## Documentación incluida

| Documento | Contenido |
|---|---|
| [Requisitos del Lenguaje Origen](Documentacion/RequisitosLenguajeOrigen.md) | Vocabulario, operadores, delimitadores y equivalencias con TypeScript |
| [Gramática BNF](Documentacion/BNF.md) | Gramática LL(1) en BNF, conjuntos FIRST/FOLLOW, verificación y ajustes |
| `README.md` | Instalación, ejecución, estructura y descripción de todos los módulos |

---

## Estructura del proyecto

```
compilador/
├── Main.py                        # Menú principal (Entregas 1–4)
├── lexico/
│   ├── Tokens.py                  # Enum TokenType (33 tokens) y dataclass Token
│   ├── Lexer.py                   # Analizador léxico reutilizable
│   └── LogicaLexer.py             # EstadoLexer — lógica de estado para la GUI léxica
├── sintactico/
│   ├── Gramatica.py               # Gramática LL(1) factorizada y funciones auxiliares
│   ├── TablaLL1.py                # Cálculo de FIRST, FOLLOW y tabla LL(1)
│   ├── EstadoParser.py            # Instancia global de tabla y conjuntos
│   ├── ArbolSintactico.py         # NodoArbol, ResultadoAnalisis, ErrorSintactico
│   ├── RecuperacionErrores.py     # Tokens de sincronización y salto en modo pánico
│   ├── ParserRecursivo.py         # Analizador descendente recursivo
│   ├── ParserPredictivo.py        # Analizador predictivo LL(1) con pila explícita
│   └── ControladorParser.py       # SolicitudAnalisis / EjecutarAnalisis — API unificada
├── semantico/
│   ├── TablaSimbolos.py           # EntradaSimbolo, AmbitoTabla, TablaSimbolos (ámbitos anidados)
│   ├── ErrorSemantico.py          # ErrorSemantico, ResultadoSemantico, constantes de tipo
│   ├── AnalizadorSemantico.py     # Visitor sobre el AST — implementa las 5 reglas semánticas
│   └── ControladorSemantico.py    # EjecutarAnalisisSemantico — API unificada (léxico+sint+sem)
├── ia/
│   └── SugerenciasIA.py           # Clasificador Naive Bayes para sugerencias de error sintáctico
└── gui/
    ├── Estilos.py                 # Paleta TEMA unificada para todas las interfaces
    ├── Programas.py               # Programas de prueba predefinidos (Entregas 1–3)
    ├── InterfazLexer.py           # Interfaz Tkinter — Entrega 1
    ├── InterfazSintactico.py      # Interfaz Tkinter — Entregas 2 y 3
    └── InterfazSemantico.py       # Interfaz Tkinter — Entrega 4
```

---

## Requisitos e instalación

- Python 3.9 o superior
- `tkinter` — incluido en Python estándar. En Linux: `sudo apt install python3-tk`
- Sin dependencias externas adicionales

```bash
git clone https://github.com/DanielPuertaBernal/compilador
cd compilador

# Entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate       # Mac / Linux
venv\Scripts\activate          # Windows

# Ejecutar
python Main.py
```

---

## Uso de la aplicación

### Menú principal

`Main.py` muestra cuatro tarjetas de acceso rápido:

| Opción | Atajo | Descripción |
|---|---|---|
| Analizador Léxico | `1` | Interfaz de la Entrega 1 |
| Analizador Sintáctico | `2` | Interfaz de la Entrega 2 |
| Recuperación de Errores + IA | `3` | Interfaz de la Entrega 3 (recuperación activada) |
| Analizador Semántico | `4` | Interfaz de la Entrega 4 |

### Entrega 1 — Analizador léxico

Seleccionar preset o escribir código. Botones disponibles:

| Botón | Función |
|---|---|
| **Analizar todo** | Tokeniza de una sola vez |
| **Paso siguiente** | Avanza un token — modo paso a paso |
| **Reiniciar** | Limpia el análisis |

Panel derecho muestra el código resaltado por categoría y la tabla de símbolos léxicos.

### Entrega 2 — Analizador sintáctico

| Funcionalidad | Descripción |
|---|---|
| Método | Elegir entre **recursivo** y **predictivo LL(1)** |
| Árbol sintáctico | Visualización del árbol generado |
| Traza predictiva | Pila, lookahead y acción paso a paso |
| Tabla LL(1) | Calculada automáticamente desde la gramática |
| FIRST / FOLLOW | Conjuntos mostrados en la propia app |

### Entrega 3 — Recuperación de errores + IA

Activar **"Recuperar errores (E3)"** antes de analizar. El parser no aborta al primer error: salta tokens hasta el siguiente punto de sincronización y sigue. La pestaña **Errores (E3)** muestra todos los errores encontrados con número, fila, columna y la sugerencia generada por el modelo de IA.

### Entrega 4 — Analizador semántico

Seleccionar un ejemplo de los 7 presets o escribir código propio y pulsar **Analizar**. La interfaz expone cuatro pestañas:

| Pestaña | Contenido |
|---|---|
| **Resumen** | Veredicto del análisis, reglas aplicadas y cantidad de errores |
| **Tabla de Símbolos** | Todos los identificadores declarados con tipo, ámbito, fila y columna |
| **Errores Semánticos** | Lista detallada: regla violada, lexema, posición y sugerencia de corrección |
| **Árbol** | Árbol sintáctico generado por el parser (misma representación que E2/E3) |

Los 7 programas de ejemplo cubren:

| Preset | Regla demostrada |
|---|---|
| Sin errores (factorial) | Programa válido — 0 errores |
| Doble declaración | REGLA SEM 1 |
| Variable no declarada | REGLA SEM 2 |
| Tipo incompatible | REGLA SEM 3 |
| Retorno incompatible | REGLA SEM 4 |
| Función no declarada | REGLA SEM 5 |
| Errores mixtos | Varias reglas simultáneas |

---

## Reglas semánticas — Entrega 4

El módulo `semantico/AnalizadorSemantico.py` implementa un **visitor** sobre el AST producido por el parser. Cada nodo relevante es visitado por su método `_visitar_<nonterminal>` correspondiente.

### REGLA SEM 1 — No redeclaración en el mismo ámbito

**Tipo de atributo:** sintetizado — al declarar una variable/función/parámetro se consulta si el nombre ya existe en el ámbito actual con `buscar_local`.

**Restricción:** un identificador no puede declararse dos veces en el mismo ámbito. Los ámbitos anidados sí pueden sombrear nombres de ámbitos padres.

**Detección:** `_visitar_decl_variable`, `_visitar_decl_atributo`, `_visitar_def_funcion`, `_visitar_sent_para` — todos invocan `tabla.buscar_local` antes de `tabla.declarar`.

---

### REGLA SEM 2 — Uso de variable previamente declarada

**Tipo de atributo:** heredado — el nombre del identificador se propaga hacia arriba en la jerarquía de ámbitos.

**Restricción:** toda variable o parámetro usado en una expresión debe haber sido declarado previamente (en el ámbito actual o en algún ámbito padre).

**Detección:** `_visitar_valor_atomico` y `_visitar_sent_identificador` — invocan `tabla.buscar` (búsqueda ascendente) y reportan error si devuelve `None`.

---

### REGLA SEM 3 — Compatibilidad de tipos en inicialización

**Tipo de atributo:** sintetizado — el tipo de la expresión de la derecha se extrae del valor literal o de la entrada de la tabla de símbolos.

**Restricción:** en `var x: T = expr`, el tipo inferido de `expr` debe ser compatible con `T`. Los tipos permitidos son `entero`, `real`, `cadena` y `booleano`; `entero` es compatible con `real` (promoción implícita).

**Detección:** `_visitar_decl_variable` — compara `tipo_declarado` con `tipo_valor`.

---

### REGLA SEM 4 — Tipo de retorno compatible con la función

**Tipo de atributo:** heredado — el tipo de retorno de la función se guarda en `_tipo_retorno_actual` al entrar a `_visitar_def_funcion` y se pasa implícitamente a `_visitar_sent_retornar`.

**Restricción:** el tipo de la expresión devuelta en `retornar <expr>` debe ser compatible con el tipo de retorno declarado en la cabecera de la función.

**Detección:** `_visitar_sent_retornar` — compara el tipo inferido de la expresión con `_tipo_retorno_actual`.

---

### REGLA SEM 5 — Función o clase invocada debe estar declarada

**Tipo de atributo:** sintetizado — el nombre del callee se extrae del nodo `IDENTIFICADOR` hijo del nodo de llamada.

**Restricción:** toda llamada a función o instanciación de clase requiere que el identificador haya sido declarado como `funcion` o `clase` en un ámbito visible.

**Detección:** `_visitar_sent_identificador` — cuando detecta paréntesis tras el identificador verifica que la entrada en la tabla tenga `categoria == "funcion"` o `"clase"`.

---

### Tabla de símbolos — estructura

```
TablaSimbolos
  └── AmbitoTabla "global"
        ├── EntradaSimbolo (variable / funcion / clase)
        └── AmbitoTabla "miFunc"          ← sub-ámbito al entrar en función
              ├── EntradaSimbolo (parametro)
              └── AmbitoTabla "para_i"    ← sub-ámbito al entrar en ciclo para
                    └── EntradaSimbolo (variable entera de iteración)
```

La búsqueda ascendente (`buscar`) recorre la cadena de padres hasta el ámbito `"global"`. La declaración siempre opera en el ámbito actual (`buscar_local` + `declarar`).

---

## Módulo de IA — Sugerencias contextuales (Entrega 3)

**Archivo:** [`ia/SugerenciasIA.py`](ia/SugerenciasIA.py)

### ¿Qué problema resuelve?

Cuando el parser detecta un error, el mensaje genérico ("token inesperado") no orienta al estudiante. El modelo de IA clasifica el contexto del error y devuelve un mensaje en lenguaje natural específico, por ejemplo:

> *"Falta la palabra reservada `entonces` después de la condición del `si`."*

### Algoritmo: Naive Bayes Multinomial

Se eligió Naive Bayes Multinomial por ser interpretable, liviano (sin dependencias externas), entrenable incrementalmente y apropiado para clasificación de texto con características discretas.

#### Paso 1 — Extracción de características

Cada error se describe con tres tipos de características categóricas:

```
NT:<nonterminal>     →  el no-terminal que se estaba expandiendo
FOUND:<token>        →  el terminal encontrado (inesperado)
EXP:<token>          →  cada terminal esperado en ese contexto (uno por característica)
```

**Ejemplo** — error al parsear `sent_si` con token `fin_si` esperando `entonces`:

```
("NT:sent_si", "FOUND:fin_si", "EXP:entonces")
```

Función: `_ExtraerCaracteristicas(nonterminal, token_encontrado, esperado) → tuple[str, ...]`

#### Paso 2 — Entrenamiento

El modelo se entrena con `DATOS_PREENTRENAMIENTO`: 60+ ejemplos etiquetados de la forma `(nonterminal, token_encontrado, [esperados], clase)`.

Por cada ejemplo, `EntrenarEjemplo` actualiza tres contadores:

| Contador | Qué almacena |
|---|---|
| `_conteos_caracteristicas[(caract, clase)]` | Cuántas veces aparece cada característica en cada clase |
| `_conteos_clases[clase]` | Cuántos ejemplos hay de cada clase |
| `_vocabulario` | Conjunto de todas las características vistas |

Las 15 clases posibles son: `falta_entonces`, `falta_hacer`, `falta_fin_si`, `falta_fin_para`, `falta_fin_mientras`, `falta_fin_funcion`, `falta_fin_clase`, `falta_tipo`, `falta_paren_der`, `falta_dos_puntos`, `falta_asignacion`, `falta_identificador`, `falta_expresion`, `operador_invalido`, `token_inesperado`.

#### Paso 3 — Predicción

Para un nuevo error, `PredecirClase` calcula el puntaje logarítmico de cada clase:

```
score(clase) = log P(clase) + Σ log P(característica | clase)
```

Con **suavizado de Laplace** para características no vistas:

```
P(característica | clase) = (conteo(caract, clase) + 1) / (conteo(clase) + |vocabulario| + 1)
```

Se elige la clase con mayor puntaje.

```python
# Simplificado
for cls, conteo_cls in self._conteos_clases.items():
    puntaje = log(conteo_cls / self._total)             # prior
    for caract in caracteristicas:
        conteo = conteos[(caract, cls)]                 # likelihood + Laplace
        puntaje += log((conteo + 1) / (conteo_cls + vocab_size))
```

#### Paso 4 — Traducción a lenguaje natural

La clase predicha se mapea a un mensaje en `MENSAJES_SUGERENCIA`:

```python
MENSAJES_SUGERENCIA = {
    "falta_entonces":  "Falta la palabra reservada `entonces` después de la condición del `si`.",
    "falta_fin_si":    "Falta `fin_si` para cerrar el bloque condicional.",
    # ... 15 clases en total
}
```

#### Paso 5 — Persistencia del modelo

Al iniciarse, `_CargarOConstruir` intenta cargar `suggestion_model.json`. Si no existe (o falla), construye el modelo desde `DATOS_PREENTRENAMIENTO` y lo guarda. Esto evita reentrenar en cada ejecución.

```
Primera ejecución:  DATOS_PREENTRENAMIENTO → ModeloSugerencias → suggestion_model.json
Siguientes:         suggestion_model.json → ModeloSugerencias (carga rápida)
```

`suggestion_model.json` está en `.gitignore` — se regenera automáticamente.

#### Diagrama de flujo completo

```
Parser detecta error
        │
        ▼
ConstruirError(nonterminal, token_encontrado, esperados)
        │
        ▼
MODELO_IA.Sugerir(nonterminal, encontrado, esperados)
        │
        ▼
_ExtraerCaracteristicas → ["NT:sent_si", "FOUND:fin_si", "EXP:entonces"]
        │
        ▼
PredecirClase → score por cada clase (Naive Bayes + Laplace)
        │
        ▼
clase = "falta_entonces"
        │
        ▼
MENSAJES_SUGERENCIA["falta_entonces"]
        │
        ▼
"Falta la palabra reservada `entonces` después de la condición del `si`."
        │
        ▼
ErrorSintactico.sugerencia → mostrado en pestaña Errores (E3)
```

### Reentrenar o extender el modelo

```python
from ia.SugerenciasIA import ModeloSugerencias

modelo = ModeloSugerencias.Cargar("ia/suggestion_model.json")
modelo.EntrenarEjemplo("sent_si", "fin_clase", ["entonces"], "falta_entonces")
modelo.Guardar("ia/suggestion_model.json")
```

---

## Entregables por entrega

### Entrega 1

| Entregable | Evidencia |
|---|---|
| Código fuente Python | `lexico/Tokens.py`, `lexico/Lexer.py`, `gui/InterfazLexer.py` |
| Interfaz gráfica | `gui/InterfazLexer.py` — resaltado, tabla léxica, modo paso a paso |

### Entrega 2

| Entregable | Evidencia |
|---|---|
| Parser recursivo | `sintactico/ParserRecursivo.py` |
| Parser predictivo LL(1) | `sintactico/ParserPredictivo.py` |
| Tabla LL(1) calculada | `sintactico/TablaLL1.py`, pestaña "Tabla LL(1)" en la GUI |
| FIRST / FOLLOW | `sintactico/TablaLL1.py`, pestaña "FIRST/FOLLOW" en la GUI |
| Árbol sintáctico | Pestaña "Árbol" en `gui/InterfazSintactico.py` |
| Ajustes a la gramática | §8 de `Documentacion/BNF.md` |

### Entrega 3

| Entregable | Evidencia |
|---|---|
| Recuperación en modo pánico | `sintactico/RecuperacionErrores.py`, checkbox "Recuperar errores (E3)" |
| Múltiples errores por análisis | `sintactico/ParserRecursivo.py` y `ParserPredictivo.py` con `recuperar=True` |
| Sugerencias con IA | `ia/SugerenciasIA.py` — Naive Bayes Multinomial con suavizado de Laplace |
| Pestaña de errores detallada | "Errores (E3)" en `gui/InterfazSintactico.py` |

### Entrega 4

| Entregable | Evidencia |
|---|---|
| ≥ 5 reglas semánticas | `semantico/AnalizadorSemantico.py` — REGLAS SEM 1–5 documentadas |
| Atributos sintetizados/heredados | Comentarios `# Atributo sintetizado/heredado` en cada `_visitar_*` |
| Tabla de símbolos con ámbitos anidados | `semantico/TablaSimbolos.py` — jerarquía padre/hijo + búsqueda ascendente |
| Detección con fila/columna/lexema/mensaje | `semantico/ErrorSemantico.py` — `FormatearReporte()` + columnas en GUI |
| Recuperación tras error (continúa el análisis) | `_registrar_error` no lanza excepción; el analizador siempre termina |
| Separación de fases (semántico ≠ sintáctico) | Paquete `semantico/` independiente; recibe el AST ya construido |
| GUI con tabla de símbolos + errores + árbol | `gui/InterfazSemantico.py` — 4 pestañas: Resumen, Símbolos, Errores, Árbol |
| 7 programas de demostración | `PROGRAMAS_SEM` en `gui/InterfazSemantico.py` (uno por regla + mixto) |

---

## Tecnologías

- **Python 3.9+** con `tkinter` para la GUI
- **Sin dependencias externas** — Naive Bayes implementado desde cero con `math.log`; semántico implementado con el patrón Visitor sobre el AST
- **LL(1)** verificado sin conflictos — tabla calculada en `sintactico/TablaLL1.py`
